import { forwardRef } from 'react';
import styles from './Input.module.scss';

export const Input = forwardRef(({ 
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  className = '',
  ...props 
}, ref) => {
  const hasError = Boolean(error);

  return (
    <div className={`${styles.wrapper} ${className}`}>
      {label && (
        <label className={styles.label} htmlFor={props.id}>
          {label}
        </label>
      )}
      
      <div className={styles.inputContainer}>
        {leftIcon && (
          <span className={styles.leftIcon}>
            {leftIcon}
          </span>
        )}
        
        <input
          ref={ref}
          className={`${styles.input} ${hasError ? styles.error : ''} ${leftIcon ? styles.hasLeftIcon : ''} ${rightIcon ? styles.hasRightIcon : ''}`}
          {...props}
        />
        
        {rightIcon && (
          <span className={styles.rightIcon}>
            {rightIcon}
          </span>
        )}
      </div>
      
      {(error || helperText) && (
        <p className={`${styles.helperText} ${hasError ? styles.errorText : ''}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';