const form = document.querySelector('#search-form');
const status = document.querySelector('#status');
const results = document.querySelector('#results');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  status.textContent = 'Searching stores… this can take a moment.';
  results.hidden = true;
  const budgetValue = document.querySelector('#budget').value;
  const payload = {
    query: document.querySelector('#query').value,
    size: document.querySelector('#size').value || null,
    budget: budgetValue ? Number(budgetValue) : null,
  };
  try {
    const response = await fetch('/api/search', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Search failed');
    status.textContent = `Source results for: ${data.query}`;
    results.textContent = data.answer;
    results.hidden = false;
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
});
