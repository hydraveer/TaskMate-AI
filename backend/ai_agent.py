from openai import OpenAI
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import dateparser
from dotenv import load_dotenv

load_dotenv()  

from ai_tools import get_tools
import crud
from sqlalchemy.orm import Session


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_due_date(date_string: Optional[str]) -> Optional[datetime]:

    if not date_string:
        return None

    try:
        parsed_date = dateparser.parse(          
            date_string,
            settings={'PREFER_DATES_FROM': 'future'}
        )
        return parsed_date                        
    except (ValueError, Exception):
        return None

def execute_function(function_name: str, arguments: Dict[str, Any], db: Session, user_id: int):
    if function_name == "create_task":
        due_date = parse_due_date(arguments.get("due_date"))

        task = crud.create_task(
            db=db,
            user_id=user_id,
            title=arguments.get("title"),
            description=arguments.get("description"),
            due_date=due_date,
            priority=arguments.get("priority", "medium"),
        )
        return {
            "success": True,
            "message": f"Task is created with ID {task.id}",
            "task": task.to_dict()
        }

        # LIST TASKS
    elif function_name == "list_tasks":
        completed = arguments.get("completed")
        
        tasks = crud.get_all_tasks(
            db=db,
            user_id=user_id,
            completed=completed
        )
        
        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks)
        }
    
    # UPDATE TASK
    elif function_name == "update_task":
        task_id = arguments["task_id"]
        
        # Parse due date if provided
        due_date = parse_due_date(arguments.get("due_date")) if "due_date" in arguments else None
        
        task = crud.update_task(
            db=db,
            task_id=task_id,
            user_id=user_id,
            title=arguments.get("title"),
            description=arguments.get("description"),
            due_date=due_date,
            completed=arguments.get("completed"),
            priority=arguments.get("priority")
        )
        
        if task:
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Task {task_id} updated"
            }
        else:
            return {
                "success": False,
                "message": "Task not found"
            }
    
    # DELETE TASK
    elif function_name == "delete_task":
        task_id = arguments["task_id"]
        
        success = crud.delete_task(
            db=db,
            task_id=task_id,
            user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Task {task_id} deleted"
            }
        else:
            return {
                "success": False,
                "message": "Task not found"
            }
    
    # SEARCH TASKS
    elif function_name == "search_tasks":
        query = arguments["query"]
        
        tasks = crud.search_tasks(
            db=db,
            user_id=user_id,
            query=query
        )
        
        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks),
            "query": query
        }
    
    # Unknown function
    else:
        return {
            "success": False,
            "message": f"Unknown function: {function_name}"
        }

def chat_with_ai(message: str, db: Session, user_id: int, conversation_history: list = None) -> str:
    """Main function to chat with AI and execute functions"""
    
    if conversation_history is None:
        conversation_history = []
    
    system_message = {
        "role": "system",
        "content": """You are a task management assistant. 

When user asks to complete/update/delete tasks:
1. FIRST call list_tasks to get task IDs
2. THEN call update_task/delete_task with the task_id

IMPORTANT: After calling list_tasks and seeing the task_id, 
you MUST call the update/delete function in the SAME conversation.

Current date: """ + datetime.now().strftime("%Y-%m-%d")
    }
    
    messages = [system_message] + conversation_history + [
        {"role": "user", "content": message}
    ]
    
    tools = get_tools()
    
    # Loop up to 3 times to allow multiple function calls
    max_iterations = 3
    for iteration in range(max_iterations):
        print(f"\n🔄 Iteration {iteration + 1}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check if AI wants to use tools
        if assistant_message.tool_calls:
            print(f"🤖 Tool calls: {len(assistant_message.tool_calls)}")
            
            # Add assistant message
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Execute each function
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"⚙️ Executing: {function_name}({arguments})")
                
                function_result = execute_function(function_name, arguments, db, user_id)
                
                print(f"✅ Result: {function_result.get('message', 'Done')}")
                
                # Add function result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
            
            # Continue loop - AI might want to call more functions
            continue
        
        else:
            # AI responded with text - we're done!
            print(f"💬 Final response")
            return assistant_message.content
    
    print("⚠️ Max iterations reached")
    return "I've processed your request. Please check your tasks."