import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  variant = 'default',
  size = 'default',
  disabled = false,
  className = '',
  ...props 
}) => {
  const variantClasses = {
    default: '',
    primary: 'button-primary',
    success: 'button-success',
    warning: 'button-warning',
    danger: 'button-danger',
  };
  
  const sizeClasses = {
    small: 'button-small',
    default: '',
    large: 'button-large',
  };
  
  const classes = [
    'button',
    variantClasses[variant],
    sizeClasses[size],
    disabled ? 'button-disabled' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;