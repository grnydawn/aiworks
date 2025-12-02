import argparse
import logging
from config import Config
from utils import setup_logging
from workflow import WorkflowEngine

def main():
    parser = argparse.ArgumentParser(description="Operational TRITON Workflow")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--mode", choices=["daemon", "run-once"], default="run-once", help="Operation mode")
    parser.add_argument("--date", help="Date to process (YYYY-MM-DD) for run-once mode")
    
    args = parser.parse_args()

    # Setup
    config = Config(args.config)
    setup_logging(log_dir=config.get("global.log_dir"))
    logger = logging.getLogger(__name__)

    engine = WorkflowEngine(config)

    if args.mode == "daemon":
        engine.start_daemon()
    elif args.mode == "run-once":
        if not args.date:
            logger.error("--date is required for run-once mode")
            return
        engine.run_pipeline(args.date)

if __name__ == "__main__":
    main()
