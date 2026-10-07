// Disable duplicate submissions without losing the clicked action's value.
document.querySelectorAll('[data-doi-form]').forEach((form) => {
  let pending = false;
  form.addEventListener('submit', (event) => {
    if (pending) {
      event.preventDefault();
      return;
    }
    const button = event.submitter;
    if (!button) return;
    pending = true;
    const action = document.createElement('input');
    action.type = 'hidden';
    action.name = button.name;
    action.value = button.value;
    action.dataset.pendingAction = '';
    form.append(action);
    form.querySelectorAll('button[type="submit"]').forEach((control) => {
      control.disabled = true;
    });
    button.textContent = button.dataset.pending;
  });
  // Browser Back may restore a cached page with its controls still disabled.
  const labels = new Map([...form.querySelectorAll('button[type="submit"]')]
    .map((button) => [button, button.textContent]));
  window.addEventListener('pageshow', () => {
    pending = false;
    form.querySelectorAll('[data-pending-action]').forEach((input) => input.remove());
    labels.forEach((label, button) => {
      button.disabled = false;
      button.textContent = label;
    });
  });
});
