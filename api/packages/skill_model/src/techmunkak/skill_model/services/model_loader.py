import io
import json
import logging
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

import spacy
from spacy.language import Language
from techmunkak.core import storage

logger = logging.getLogger(__name__)

def save_model(nlp: spacy.Language):
    version = datetime.now().strftime("v%Y%m%d-%H%M%S")
    with tempfile.TemporaryDirectory() as tmp:
        model_dir = Path(tmp) / version
        nlp.to_disk(model_dir)
        archive = _archive_model(model_dir)
        
    key = storage.put_ner_model(version, data=archive)
    logger.info("model uploaded to %s", key)
    return version
    
def get_model() -> Language:    
    version = _current_version()
    model_dir = Path(f"/tmp/models/ner/{version}")
    if not model_dir.is_dir():        
        model_dir.parent.mkdir(parents=True, exist_ok=True)
        resp = storage.get_ner_model(version)
    
        with tarfile.open(fileobj=io.BytesIO(resp), mode="r:gz") as tar:
            tar.extractall(model_dir.parent, filter="data")
        
    return spacy.load(model_dir)

def _archive_model(model_dir: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(model_dir, arcname=model_dir.name)
    
    return buf.getvalue()

def _current_version() -> str:
    json_str = storage.get_ner_model_version()
    data = json.loads(json_str)
    
    assert "version" in data, f"unable to read current model version: {json_str}"

    return data["version"]