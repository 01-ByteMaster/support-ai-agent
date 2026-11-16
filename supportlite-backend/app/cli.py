import argparse
from app.database import init_db
from app.config import settings
from app.services.ingestion import ingest_directory
def main():
    p=argparse.ArgumentParser();p.add_argument("command",choices=["ingest","init-db"]);a=p.parse_args();init_db()
    if a.command=="ingest":
        r=ingest_directory(settings.knowledge_base_path);print(r.model_dump_json(indent=2))
        if r.failed:raise SystemExit(1)
if __name__=="__main__":main()
