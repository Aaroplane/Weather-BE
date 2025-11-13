import { SEVERITY_COLORS } from '../../../utils/constants';
import styles from './SuggestionCard.module.scss';

export const SuggestionCard = ({ suggestion }) => {
  const { icon, severity, suggestion: text } = suggestion;
  
  return (
    <div className={`${styles.card} ${styles[severity]}`}>
      <span className={styles.icon}>{icon}</span>
      <div className={styles.content}>
        <span className={styles.severity}>
          {severity.toUpperCase()} Priority
        </span>
        <p className={styles.text}>{text}</p>
      </div>
    </div>
  );
};