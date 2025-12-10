import { useState, useEffect, useCallback } from 'react';
import { tasksAPI } from '../services/api';

export default function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ title: '', description: '', priority: 'medium', status: 'pending' });
  const [editingId, setEditingId] = useState(null);

  const loadTasks = useCallback(async () => {
    try {
      const res = await tasksAPI.getTasks(filters);
      setTasks(res.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleSearch = async () => {
    if (!search.trim()) {
      loadTasks();
      return;
    }
    try {
      const res = await tasksAPI.searchTasks(search);
      setTasks(res.data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await tasksAPI.updateTask(editingId, formData);
      } else {
        await tasksAPI.createTask(formData);
      }
      setFormData({ title: '', description: '', priority: 'medium', status: 'pending' });
      setShowForm(false);
      setEditingId(null);
      loadTasks();
    } catch (error) {
      alert('Failed to save task');
    }
  };

  const handleEdit = (task) => {
    setFormData({ title: task.title, description: task.description || '', priority: task.priority, status: task.status });
    setEditingId(task.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this task?')) {
      try {
        await tasksAPI.deleteTask(id);
        loadTasks();
      } catch (error) {
        alert('Failed to delete task');
      }
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="task-container">
      <div className="task-header">
        <h2>My Tasks</h2>
        <button onClick={() => { setShowForm(!showForm); setEditingId(null); setFormData({ title: '', description: '', priority: 'medium', status: 'pending' }); }}>
          {showForm ? 'Cancel' : 'New Task'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="task-form">
          <input
            type="text"
            placeholder="Task title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <select value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })}>
            <option value="pending">Pending</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          <button type="submit">{editingId ? 'Update' : 'Create'} Task</button>
        </form>
      )}

      <div className="filters">
        <input
          type="text"
          placeholder="Search tasks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch}>Search</button>
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="in-progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
        <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
          <option value="">All Priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="task-list">
        {tasks.length === 0 ? (
          <p>No tasks found. Create one to get started!</p>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="task-item">
              <div className="task-content">
                <h3>{task.title}</h3>
                {task.description && <p>{task.description}</p>}
                <div className="task-meta">
                  <span className={`badge priority-${task.priority}`}>{task.priority}</span>
                  <span className={`badge status-${task.status}`}>{task.status}</span>
                </div>
              </div>
              <div className="task-actions">
                <button onClick={() => handleEdit(task)}>Edit</button>
                <button onClick={() => handleDelete(task.id)} className="delete">Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
