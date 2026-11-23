// Лабораторная работа №6: Скрипты клиентской части
document.addEventListener('DOMContentLoaded', () => {
    // Автоматическое скрытие flash-уведомлений через 5 секунд
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Подтверждение удаления
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const msg = form.getAttribute('data-confirm') || 'Вы действительно хотите выполнить удаление?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});
