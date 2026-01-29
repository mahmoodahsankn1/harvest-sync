/* JS Module: UI - Handles Role-based UI Logic */

export const getRole = () => {
    return document.body.getAttribute('data-role') || 'guest';
};

export const initUI = () => {
    const role = getRole();
    console.log(`Initializing UI for role: ${role}`);

    // Example: Update document title or specific elements based on role
    updateThemeColor(role);
};

const updateThemeColor = (role) => {
    const root = document.documentElement;
    // Colors are already handled in CSS variables, but we can do dynamic meta tags here
    const roleColors = {
        farmer: '#F59E0B',
        user: '#0EA5E9',
        worker: '#475569',
        govt: '#6366F1'
    };

    if (roleColors[role]) {
        // Update meta theme-color if it exists
        let metaThemeColor = document.querySelector("meta[name=theme-color]");
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = "theme-color";
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = roleColors[role];
    }
};
