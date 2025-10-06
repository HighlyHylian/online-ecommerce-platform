// Basic Login Form Script
class BasicLoginForm {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.passwordToggle = document.getElementById('passwordToggle');
        this.successMessage = document.getElementById('successMessage');
        
        this.init();
    }
    
    init() {
        // Initialize shared utilities
        FormUtils.addSharedAnimations();
        FormUtils.setupFloatingLabels(this.form);
        FormUtils.setupPasswordToggle(this.passwordInput, this.passwordToggle);
        
        // Add event listeners
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.usernameInput.addEventListener('input', () => this.validateField('username'));
        this.passwordInput.addEventListener('input', () => this.validateField('password'));
        
        // Add entrance animation
        FormUtils.addEntranceAnimation(this.form.closest('.login-card'), 100);
    }
    
    validateField(fieldName) {
        const input = document.getElementById(fieldName);
        const value = input.value.trim();
        let validation;
        
        // Clear previous errors
        FormUtils.clearError(fieldName);
        
        // Validate based on field type
        if (fieldName === 'username') {
            validation = FormUtils.validateUsername(value);
        } else if (fieldName === 'password') {
            validation = FormUtils.validatePassword(value);
        }
        
        if (!validation.isValid && value !== '') {
            FormUtils.showError(fieldName, validation.message);
            return false;
        } else if (validation.isValid) {
            FormUtils.showSuccess(fieldName);
            return true;
        }
        
        return true;
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value.trim();
        
        // Validate all fields
        const usernameValid = this.validateField('username');
        const passwordValid = this.validateField('password');
        
        if (!usernameValid || !passwordValid) {
            FormUtils.showNotification('Please fix the errors below', 'error', this.form);
            return;
        }
        
        // Show loading state
        const submitBtn = this.form.querySelector('.login-btn');
        submitBtn.classList.add('loading');
        
        try {
            // Simulate login process
            await FormUtils.simulateLogin(username, password);
            
            // Show success state
            this.showSuccess();
            
        } catch (error) {
            // Show error notification
            FormUtils.showNotification(error.message, 'error', this.form);
        } finally {
            // Remove loading state
            submitBtn.classList.remove('loading');
        }
    }
    
    showSuccess() {
        // Hide the form
        this.form.style.display = 'none';
        
        // Show success message
        this.successMessage.classList.add('show');
        
        // Simulate redirect after 2 seconds
        setTimeout(() => {
            FormUtils.showNotification('Redirecting to dashboard...', 'success', this.successMessage);
        }, 2000);
    }
}

// Initialize the form when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BasicLoginForm();
});