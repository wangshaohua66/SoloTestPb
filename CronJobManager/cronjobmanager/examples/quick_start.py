#!/usr/bin/env python3
"""
README快速开始示例脚本
验证README中的示例代码可以正常运行
"""

import sys
import os
import os.path as path

project_root = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.insert(0, project_root)

from datetime import datetime, timedelta
from core.scheduler import TaskScheduler
from core.models.task import TaskType


def my_task_function():
    print("Task executed successfully!")
    return "OK"


if __name__ == "__main__":
    print("=" * 60)
    print("README Quick Start Example")
    print("=" * 60)
    print()
    
    scheduler = TaskScheduler()
    
    try:
        print("[1/4] Starting scheduler...")
        scheduler.start()
        print("      [OK] Scheduler started")
        print()
        
        print("[2/4] Adding Cron task (run every minute)...")
        task1 = scheduler.add_task(
            name="Example Cron Task",
            func_path="tests.test_helpers.success_task",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        print(f"      [OK] Task added: {task1['name']} (ID: {task1['id']})")
        print()
        
        print("[3/4] Adding Interval task (run every 30 seconds)...")
        task2 = scheduler.add_task(
            name="Example Interval Task",
            func_path="tests.test_helpers.success_task",
            task_type=TaskType.INTERVAL,
            interval_seconds=30,
        )
        print(f"      [OK] Task added: {task2['name']} (ID: {task2['id']})")
        print()
        
        print("[4/4] Running task immediately to verify...")
        execution_id = scheduler.run_task_now(task1["id"])
        print(f"      [OK] Task execution started, execution ID: {execution_id}")
        print()
        
        import time
        time.sleep(1)
        
        task_status = scheduler.task_service.get_task(task1["id"])
        print(f"      [OK] Task status: {task_status['status']}")
        print()
        
        print("=" * 60)
        print("All operations completed successfully!")
        print()
        print("Task list:")
        tasks = scheduler.task_service.list_tasks()
        for task in tasks:
            print(f"  - {task['name']} (ID: {task['id']}, Type: {task['task_type']})")
        print()
        print("Script will run for 3 seconds then exit...")
        print("=" * 60)
        print()
        
        time.sleep(3)
        
        print()
        print("Exiting normally...")
        
    except KeyboardInterrupt:
        print()
        print("User interrupted, exiting...")
    except Exception as e:
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if scheduler._running:
            scheduler.stop()
            print("Scheduler stopped")
    
    print()
    print("Example script completed!")
