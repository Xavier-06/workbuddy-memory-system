#!/usr/bin/env python3
"""
vecmem.py — 本地向量记忆库

基于 ChromaDB + qwen3-embedding-8b 的语义记忆检索系统。
索引 ~/.workbuddy/memory/ 下的所有 Markdown 文件，支持增量同步和语义搜索。

用法:
  python3 vecmem.py index          # 全量索引
  python3 vecmem.py sync           # 增量同步（仅处理新增/修改文件）
  python3 vecmem.py search "查询"  # 语义搜索
  python3 vecmem.py status         # 查看索引状态
"""

import json
import os
import re
import sys
import hashlib
import time
from pathlib import Path
from datetime import datetime

import chromadb
from openai import OpenAI


# ─── 配置 ───────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
SYNC_STATE_PATH = SCRIPT_DIR / ".sync_state.json"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    # 展开 ~ 路径
    cfg["chroma"]["persist_dir"] = os.path.expanduser(cfg["chroma"]["persist_dir"])
    cfg["memory_dir"] = os.path.expanduser(cfg["memory_dir"])
    return cfg


# ─── Embedding 客户端 ───────────────────────────────────────────

class EmbeddingClient:
    """调用 qwen3-embedding-8b API 生成向量"""

    def __init__(self, cfg: dict):
        emb = cfg["embedding"]
        self.model = emb["model"]
        self.batch_size = emb.get("batch_size", 20)
        self.client = OpenAI(
            api_key=emb["api_key"],
            base_url=emb["base_url"],
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        """批量生成 embedding，自动分批"""
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            resp = self.client.embeddings.create(model=self.model, input=batch)
            batch_embs = [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
            all_embeddings.extend(batch_embs)
        return all_embeddings


# ─── 文档解析 ────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (metadata_dict, body_text)"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text

    fm_text = match.group(1)
    body = text[match.end() :]

    meta = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")

    return meta, body


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    超长文本切分，优先在句号/换行符等句子边界处断开，
    避免在一句话中间切断导致语义不完整。
    """
    if len(text) <= chunk_size:
        return [text]

    # 按优先级依次尝试的分隔符
    separators = ["\n\n", "\n", "。", "；", ".", ";", "，", ","]
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break

        # 在 [end - chunk_size//4, end] 范围内找最佳断点
        search_start = max(start, end - chunk_size // 4)
        best_break = -1
        for sep in separators:
            idx = text.rfind(sep, search_start, end)
            if idx > start:
                best_break = idx + len(sep)
                break

        if best_break <= start:
            # 没找到合适的断点，硬切
            best_break = end

        chunks.append(text[start:best_break])
        start = best_break - overlap if best_break > overlap else best_break

    return [c for c in chunks if c.strip()]


def chunk_document(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """
    智能分块：优先按 ## 标题切分，超长段落再按字符切分。
    短文档（< chunk_size）不分块。
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # 按 ## 标题切分
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    sections = [s for s in sections if s.strip()]

    chunks = []
    current_chunk = ""

    for section in sections:
        if len(current_chunk) + len(section) <= chunk_size:
            current_chunk += section
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # 如果单个 section 超长，优先在句子边界切分
            if len(section) > chunk_size:
                sub_chunks = _split_long_text(section, chunk_size, overlap)
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = section

    if current_chunk:
        chunks.append(current_chunk)

    return [c for c in chunks if c.strip()]


def scan_memory_files(memory_dir: str) -> list[dict]:
    """扫描 memory 目录，返回文件列表及元信息"""
    files = []
    for path in sorted(Path(memory_dir).glob("*.md")):
        name = path.name
        # MEMORY.md 也需要索引，包含长期有效的用户偏好和项目约定

        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        mtime = path.stat().st_mtime

        files.append(
            {
                "path": str(path),
                "filename": name,
                "frontmatter": fm,
                "body": body,
                "full_text": text,
                "mtime": mtime,
                "size": len(text),
                "hash": hashlib.md5(text.encode()).hexdigest(),
            }
        )
    return files


# ─── 向量存储 ────────────────────────────────────────────────────

class VectorStore:
    """ChromaDB 向量存储封装"""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        chroma_cfg = cfg["chroma"]
        self.client = chromadb.PersistentClient(path=chroma_cfg["persist_dir"])
        self.collection = self.client.get_or_create_collection(
            name=chroma_cfg["collection_name"],
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()

    def clear(self):
        name = self.cfg["chroma"]["collection_name"]
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, ids: list[str], embeddings: list[list[float]],
                      documents: list[str], metadatas: list[dict]):
        """批量添加文档，自动分批避免超限"""
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

    def delete_by_file(self, filepath: str):
        """删除指定文件的所有分块"""
        self.collection.delete(where={"source_file": filepath})

    def search(self, query_embedding: list[float], top_k: int = 5) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )


# ─── 同步状态 ────────────────────────────────────────────────────

def load_sync_state() -> dict:
    if SYNC_STATE_PATH.exists():
        with open(SYNC_STATE_PATH) as f:
            return json.load(f)
    return {}


def save_sync_state(state: dict):
    with open(SYNC_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ─── 核心操作 ────────────────────────────────────────────────────

def do_index(cfg: dict, full: bool = False):
    """全量索引 memory 目录"""
    emb_client = EmbeddingClient(cfg)
    store = VectorStore(cfg)

    if full:
        print("🗑️  清空已有索引...")
        store.clear()

    print(f"📂 扫描 {cfg['memory_dir']} ...")
    files = scan_memory_files(cfg["memory_dir"])
    print(f"   找到 {len(files)} 个记忆文件")

    all_ids = []
    all_embeddings = []
    all_documents = []
    all_metadatas = []

    for f in files:
        fm = f["frontmatter"]
        chunks = chunk_document(f["body"], cfg.get("chunk_size", 2000), cfg.get("chunk_overlap", 200))
        if not chunks:
            chunks = [f["body"] or f["full_text"]]

        print(f"   📄 {f['filename']}: {len(chunks)} 个分块")

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{f['filename']}::chunk_{idx}"
            meta = {
                "source_file": f["filename"],
                "source_path": f["path"],
                "chunk_index": idx,
                "chunk_total": len(chunks),
                "fm_name": fm.get("name", ""),
                "fm_type": fm.get("type", ""),
                "fm_description": fm.get("description", ""),
                "file_hash": f["hash"],
                "indexed_at": datetime.now().isoformat(),
            }
            all_ids.append(chunk_id)
            all_documents.append(chunk)
            all_metadatas.append(meta)

    if not all_ids:
        print("⚠️  没有可索引的文档")
        return

    print(f"\n🔮 生成 embedding（{len(all_ids)} 个分块）...")
    all_embeddings = emb_client.embed(all_documents)

    print("💾 写入 ChromaDB...")
    store.add_documents(all_ids, all_embeddings, all_documents, all_metadatas)

    # 更新同步状态
    sync_state = {}
    for f in files:
        sync_state[f["filename"]] = {"hash": f["hash"], "mtime": f["mtime"]}
    save_sync_state(sync_state)

    print(f"✅ 索引完成！共 {store.count()} 个向量")


def do_sync(cfg: dict):
    """增量同步：处理新增/修改/删除的文件"""
    emb_client = EmbeddingClient(cfg)
    store = VectorStore(cfg)
    sync_state = load_sync_state()

    print(f"📂 扫描 {cfg['memory_dir']} ...")
    files = scan_memory_files(cfg["memory_dir"])

    # 检测新增/修改
    changed = []
    for f in files:
        prev = sync_state.get(f["filename"])
        if not prev or prev["hash"] != f["hash"]:
            changed.append(f)

    # 检测删除：sync_state 里有但磁盘上没有
    disk_filenames = {f["filename"] for f in files}
    deleted = [fname for fname in sync_state if fname not in disk_filenames]

    # 清理已删除文件的向量
    if deleted:
        for fname in deleted:
            store.delete_by_file(fname)
            del sync_state[fname]
        print(f"🗑️  清理 {len(deleted)} 个已删除文件的向量: {deleted}")

    if not changed and not deleted:
        print("✅ 所有文件已是最新，无需同步")
        return

    print(f"📝 检测到 {len(changed)} 个文件变更: {[f['filename'] for f in changed]}")

    # 删除旧分块
    for f in changed:
        store.delete_by_file(f["filename"])

    # 重新索引变更文件
    all_ids = []
    all_embeddings = []
    all_documents = []
    all_metadatas = []

    for f in changed:
        fm = f["frontmatter"]
        chunks = chunk_document(f["body"], cfg.get("chunk_size", 2000), cfg.get("chunk_overlap", 200))
        if not chunks:
            chunks = [f["body"] or f["full_text"]]

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{f['filename']}::chunk_{idx}"
            meta = {
                "source_file": f["filename"],
                "source_path": f["path"],
                "chunk_index": idx,
                "chunk_total": len(chunks),
                "fm_name": fm.get("name", ""),
                "fm_type": fm.get("type", ""),
                "fm_description": fm.get("description", ""),
                "file_hash": f["hash"],
                "indexed_at": datetime.now().isoformat(),
            }
            all_ids.append(chunk_id)
            all_documents.append(chunk)
            all_metadatas.append(meta)

    print(f"🔮 生成 embedding（{len(all_ids)} 个分块）...")
    all_embeddings = emb_client.embed(all_documents)

    print("💾 写入 ChromaDB...")
    store.add_documents(all_ids, all_embeddings, all_documents, all_metadatas)

    # 更新同步状态（新增/修改的写入，已删除的已在上面移除）
    for f in changed:
        sync_state[f["filename"]] = {"hash": f["hash"], "mtime": f["mtime"]}
    save_sync_state(sync_state)

    action = f"变更 {len(changed)} 个" + (f"，清理 {len(deleted)} 个" if deleted else "")
    print(f"✅ 同步完成（{action}）！当前共 {store.count()} 个向量")


def do_search(cfg: dict, query: str, top_k: int = 5, json_output: bool = False):
    """语义搜索"""
    emb_client = EmbeddingClient(cfg)
    store = VectorStore(cfg)

    if store.count() == 0:
        if json_output:
            print(json.dumps({"error": "索引为空", "results": []}, ensure_ascii=False))
        else:
            print("⚠️  索引为空，请先运行: python3 vecmem.py index")
        return

    if not json_output:
        print(f"🔍 搜索: {query}\n")

    query_emb = emb_client.embed([query])[0]
    results = store.search(query_emb, top_k=top_k)

    if not results["ids"][0]:
        if json_output:
            print(json.dumps({"query": query, "results": []}, ensure_ascii=False))
        else:
            print("未找到相关结果")
        return

    parsed = []
    for i, (doc_id, doc, meta, dist) in enumerate(
        zip(results["ids"][0], results["documents"][0],
            results["metadatas"][0], results["distances"][0])
    ):
        similarity = 1 - dist  # cosine distance → similarity
        source = meta.get("source_file", "?")
        fm_name = meta.get("fm_name", "")
        fm_type = meta.get("fm_type", "")
        chunk_idx = meta.get("chunk_index", 0)
        source_path = meta.get("source_path", "")

        parsed.append({
            "rank": i + 1,
            "id": doc_id,
            "source_file": source,
            "source_path": source_path,
            "fm_name": fm_name,
            "fm_type": fm_type,
            "chunk_index": chunk_idx,
            "similarity": round(similarity, 4),
            "content": doc,
        })

    if json_output:
        print(json.dumps({"query": query, "results": parsed}, ensure_ascii=False))
        return

    # 人类可读输出
    for r in parsed:
        label = r["fm_name"] if r["fm_name"] else r["source_file"]
        type_tag = f"[{r['fm_type']}]" if r["fm_type"] else ""
        print(f"─── #{r['rank']} {label} {type_tag} (相似度: {r['similarity']:.3f}) ───")
        print(f"    来源: {r['source_file']} (分块 {r['chunk_index']})")
        preview = r["content"].replace("\n", " ")[:300]
        if len(r["content"]) > 300:
            preview += "..."
        print(f"    内容: {preview}")
        print()


def do_status(cfg: dict):
    """查看索引状态"""
    store = VectorStore(cfg)
    sync_state = load_sync_state()

    print("📊 向量记忆库状态\n")
    print(f"   向量总数: {store.count()}")
    print(f"   同步文件数: {len(sync_state)}")
    print(f"   存储路径: {cfg['chroma']['persist_dir']}")
    print(f"   Embedding 模型: {cfg['embedding']['model']}")
    print(f"   Memory 目录: {cfg['memory_dir']}")

    # 检查文件变更
    files = scan_memory_files(cfg["memory_dir"])
    changed = []
    missing = []
    for f in files:
        prev = sync_state.get(f["filename"])
        if not prev:
            missing.append(f["filename"])
        elif prev["hash"] != f["hash"]:
            changed.append(f["filename"])

    for fname in sync_state:
        if not any(f["filename"] == fname for f in files):
            missing.append(f"{fname} (已删除)")

    if changed:
        print(f"\n   ⚠️  已变更: {changed}")
    if missing:
        print(f"   ⚠️  待同步: {missing}")
    if not changed and not missing:
        print(f"\n   ✅ 所有文件已同步")


# ─── CLI 入口 ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cfg = load_config()
    cmd = sys.argv[1].lower()

    if cmd == "index":
        full = "--full" in sys.argv
        do_index(cfg, full=full)
    elif cmd == "sync":
        do_sync(cfg)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("用法: python3 vecmem.py search <查询文本> [--json] [-k N]")
            sys.exit(1)
        args = sys.argv[2:]
        json_output = "--json" in args
        args = [a for a in args if a != "--json"]
        top_k = 5
        # 解析 -k 参数，同时从 args 中移除以避免污染 query
        clean_args = []
        i = 0
        while i < len(args):
            if args[i] == "-k" and i + 1 < len(args):
                top_k = int(args[i + 1])
                i += 2
            else:
                clean_args.append(args[i])
                i += 1
        query = " ".join(clean_args)
        do_search(cfg, query, top_k=top_k, json_output=json_output)
    elif cmd == "status":
        do_status(cfg)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
