export function showFormMessage(form, msg, color = 'red') {
    let msgElem = form.querySelector('.form-message');
    if (!msgElem) {
        msgElem = document.createElement('div');
        msgElem.className = 'form-message';
        form.appendChild(msgElem);
    }
    msgElem.textContent = msg;
    msgElem.style.color = color;
}