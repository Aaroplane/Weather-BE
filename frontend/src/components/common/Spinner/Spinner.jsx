import styles from './Spinner.module.scss';

export const Spinner = ({ size = 'md', color = 'primary', className = '' }) => {
  return (
    <div className={`${styles.spinner} ${styles[size]} ${styles[color]} ${className}`}>
      <div className={styles.circle} />
    </div>
  );
};