const API_URL = 'http://localhost:5000';

export const jobsApi = {
  getJobs: async () => {
    const response = await fetch(`${API_URL}/api/jobs`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.json();
  },

  getJob: async (jobId: number) => {
    const response = await fetch(`${API_URL}/api/jobs/${jobId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.json();
  },

  applyForJob: async (jobId: number) => {
    const response = await fetch(`${API_URL}/api/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.json();
  },
}; 