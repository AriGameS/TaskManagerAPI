#!/bin/bash

# Simple curl-based API tests
# Make sure the API is running on localhost:5125 before running this script

BASE_URL="http://localhost:5125"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting curl-based API tests..."
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health check
echo "Test 1: Health check"
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api")
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP $response)${NC}"
    exit 1
fi

# Test 2: Create a task
echo "Test 2: Create a task"
task_response=$(curl -s -X POST "$BASE_URL/tasks" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Curl Test Task",
        "description": "Task created via curl test",
        "priority": "high",
        "due_date": "2025-12-31 23:59:59"
    }')

if echo "$task_response" | grep -q "Task created successfully"; then
    echo -e "${GREEN}✓ Task creation passed${NC}"
    task_id=$(echo "$task_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo "Created task ID: $task_id"
else
    echo -e "${RED}✗ Task creation failed${NC}"
    echo "Response: $task_response"
    exit 1
fi

# Test 3: Get all tasks
echo "Test 3: Get all tasks"
tasks_response=$(curl -s "$BASE_URL/tasks")
if echo "$tasks_response" | grep -q "Curl Test Task"; then
    echo -e "${GREEN}✓ Get tasks passed${NC}"
else
    echo -e "${RED}✗ Get tasks failed${NC}"
    echo "Response: $tasks_response"
    exit 1
fi

# Test 4: Update task
echo "Test 4: Update task"
update_response=$(curl -s -X PUT "$BASE_URL/tasks/$task_id" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Updated Curl Test Task",
        "priority": "medium"
    }')

if echo "$update_response" | grep -q "Task updated successfully"; then
    echo -e "${GREEN}✓ Task update passed${NC}"
else
    echo -e "${RED}✗ Task update failed${NC}"
    echo "Response: $update_response"
    exit 1
fi

# Test 5: Complete task
echo "Test 5: Complete task"
complete_response=$(curl -s -X POST "$BASE_URL/tasks/$task_id/complete")
if echo "$complete_response" | grep -q "Task marked as completed"; then
    echo -e "${GREEN}✓ Task completion passed${NC}"
else
    echo -e "${RED}✗ Task completion failed${NC}"
    echo "Response: $complete_response"
    exit 1
fi

# Test 6: Get statistics
echo "Test 6: Get statistics"
stats_response=$(curl -s "$BASE_URL/tasks/stats")
if echo "$stats_response" | grep -q "total_tasks"; then
    echo -e "${GREEN}✓ Get statistics passed${NC}"
else
    echo -e "${RED}✗ Get statistics failed${NC}"
    echo "Response: $stats_response"
    exit 1
fi

# Test 7: Filter by status
echo "Test 7: Filter by status"
filter_response=$(curl -s "$BASE_URL/tasks?status=completed")
if echo "$filter_response" | grep -q "Updated Curl Test Task"; then
    echo -e "${GREEN}✓ Status filtering passed${NC}"
else
    echo -e "${RED}✗ Status filtering failed${NC}"
    echo "Response: $filter_response"
    exit 1
fi

# Test 8: Delete task
echo "Test 8: Delete task"
delete_response=$(curl -s -X DELETE "$BASE_URL/tasks/$task_id")
if echo "$delete_response" | grep -q "Task deleted successfully"; then
    echo -e "${GREEN}✓ Task deletion passed${NC}"
else
    echo -e "${RED}✗ Task deletion failed${NC}"
    echo "Response: $delete_response"
    exit 1
fi

# Test 9: Verify task is deleted
echo "Test 9: Verify task is deleted"
final_tasks_response=$(curl -s "$BASE_URL/tasks")
if ! echo "$final_tasks_response" | grep -q "Updated Curl Test Task"; then
    echo -e "${GREEN}✓ Task deletion verification passed${NC}"
else
    echo -e "${RED}✗ Task deletion verification failed${NC}"
    echo "Response: $final_tasks_response"
    exit 1
fi

# Test 10: Error handling
echo "Test 10: Error handling"
error_response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/tasks/999")
if [ "$error_response" = "404" ]; then
    echo -e "${GREEN}✓ Error handling passed${NC}"
else
    echo -e "${RED}✗ Error handling failed (HTTP $error_response)${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}All curl tests passed!${NC}"
echo "API is working correctly."
