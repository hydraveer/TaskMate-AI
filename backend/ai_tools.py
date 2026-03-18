

def get_tools():

    tools = [
        # Tool 1: Create Task
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task for the user. Use this when user wants to add a task, create a reminder, or add something to their todo list.",
                "parameters":{
                    "type": "object",
                    "properties": {
                        "title":{
                            "type": "string",
                            "description":"The title or description of the task (e.g. 'Buy groceries', 'Call John')"
                        },
                        "description":{
                            "type": "string",
                            "description":"Optional detailed description of the task"
                        },
                        "due_date":{
                            "type": "string",
                            "description":"When the task is due in natural language (e.g. 'tomorrow', 'next monday', '2025-01-01')"
                        },
                        "priority":{
                            "type": "string",
                            "description":"Task priority level",
                            "enum": ["low", "medium", "high"]
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        # Tool 2: List Tasks
        {
            "type": "function",
            "function": {
                "name" : "list_tasks",
                "description": "Get all tasks for the user. Use this when user asks to see their tasks, view their todo list, or check what they need to do.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean", 
                            "description": "Filter by completion status. true=completed tasks only, false=pending tasks only, null=all tasks"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 3: Update Task
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task. Use this when user wants to modify a task, mark it as complete, change priority, or update details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Mark task as completed (true) or pending (false)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "New priority level"
                        }
                    },
                    "required": ["task_id", "completed"]
                }
            }
        },
        # Tool 4: Delete Task
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task. Use this when user wants to remove or delete a task from their list.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        # Tool 5: Search Tasks
        {
            "type": "function",
            "function": {
                "name": "search_tasks",
                "description": "Search for tasks by keyword. Use this when user wants to find specific tasks containing certain words.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keyword or phrase to find in task titles and descriptions"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    return tools