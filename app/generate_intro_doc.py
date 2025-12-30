import json
import os
from web.new_intro_content import INTRO_CONTENT_FULL

# 1. 写入介绍文档.txt
doc_path = "/home/ubuntu/mindscribe-app/app/documents/介绍文档.txt"
with open(doc_path, "w", encoding="utf-8") as f:
    f.write("\n".join(INTRO_CONTENT_FULL))
print(f"已生成: {doc_path}")

# 2. 更新 metadata.json
metadata_path = "/home/ubuntu/mindscribe-app/app/documents/metadata.json"
metadata = {"active_doc_title": "介绍文档"}
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
print(f"已更新: {metadata_path}")
