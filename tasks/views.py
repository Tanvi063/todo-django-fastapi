from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date

# Create your views here.
from .models import Task
from .forms import TaskForm

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted.")
    return redirect('tasks:index')

def toggle_complete(request, task_id):
    """Toggle a task's completed status and redirect to index."""
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    messages.info(request, f"Marked as {'completed' if task.completed else 'incomplete'}: {task.title}")
    return redirect('tasks:index')

def index(request):
    """Home: create tasks (POST), list with optional search (GET ?q=), and show pending/completed sections."""
    q = request.GET.get('q', '').strip()
    queryset = Task.objects.all()
    if q:
        queryset = queryset.filter(title__icontains=q) | queryset.filter(description__icontains=q)
    tasks_pending = queryset.filter(completed=False).order_by('-created_at')
    tasks_completed = queryset.filter(completed=True).order_by('-created_at')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save()
            messages.success(request, f"Task added: {task.title}")
            return redirect('tasks:index')
    else:
        form = TaskForm()

    context = {
        'form': form,
        'q': q,
        'tasks_pending': tasks_pending,
        'tasks_completed': tasks_completed,
        'count_total': tasks_pending.count() + tasks_completed.count(),
        'count_completed': tasks_completed.count(),
        'percent_completed': int(
            round(
                (tasks_completed.count() / (tasks_pending.count() + tasks_completed.count())) * 100
            )
        ) if (tasks_pending.count() + tasks_completed.count()) > 0 else 0,
        'today': date.today(),
    }
    return render(request, 'tasks/index.html', context)

def clear_completed(request):
    """Delete all completed tasks and redirect to index."""
    count = Task.objects.filter(completed=True).count()
    if count:
        Task.objects.filter(completed=True).delete()
        messages.warning(request, f"Cleared {count} completed task(s).")
    else:
        messages.info(request, "No completed tasks to clear.")
    return redirect('tasks:index')
