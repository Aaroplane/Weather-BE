import { useState, useEffect } from "react";
import { userAPI } from "../../../api/endpoints/user";
import styles from "./FashionTips.module.scss";
import { Button } from "../../common/Button/Button"; // ← Add import at top

/**
 * Fashion recommendations component
 * Phase 1.5: Rule-based recommendations with feedback collection
 * Phase 3: AI-powered personalized suggestions
 */
const FashionTips = ({ weatherData }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  useEffect(() => {
    if (weatherData) {
      fetchRecommendations();
    }
  }, [weatherData]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await userAPI.getFashionRecommendations(weatherData);
      setRecommendations(response.recommendations);
    } catch (error) {
      console.error("Failed to fetch fashion recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedback) => {
    try {
      const tipsShown = recommendations?.tips || [];

      await userAPI.submitFashionFeedback(weatherData, tipsShown, feedback);
      setFeedbackGiven(true);
      console.log("✅ Fashion feedback submitted:", feedback);
    } catch (error) {
      console.error("Failed to submit feedback:", error);
      alert("Failed to submit feedback. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className={styles.fashionTips}>
        <div className={styles.loading}>Loading outfit suggestions...</div>
      </div>
    );
  }

  if (!recommendations) return null;

  return (
    <div className={styles.fashionTips}>
      <div className={styles.header} onClick={() => setExpanded(!expanded)}>
        <h3>👔 What to Wear</h3>
        <button
          className={styles.expandButton}
          aria-label={expanded ? "Collapse" : "Expand"}
        >
          {expanded ? "▼" : "▶"}
        </button>
      </div>

      <div className={styles.summary}>{recommendations.summary}</div>

      {expanded && (
        <div className={styles.details}>
          {/* Layers */}
          {(recommendations.layers.base.length > 0 ||
            recommendations.layers.mid.length > 0 ||
            recommendations.layers.outer.length > 0) && (
            <div className={styles.section}>
              <h4>👕 Clothing Layers</h4>
              {recommendations.layers.base.length > 0 && (
                <div className={styles.layer}>
                  <strong>Base:</strong>{" "}
                  {recommendations.layers.base.join(", ")}
                </div>
              )}
              {recommendations.layers.mid.length > 0 && (
                <div className={styles.layer}>
                  <strong>Mid:</strong> {recommendations.layers.mid.join(", ")}
                </div>
              )}
              {recommendations.layers.outer.length > 0 && (
                <div className={styles.layer}>
                  <strong>Outer:</strong>{" "}
                  {recommendations.layers.outer.join(", ")}
                </div>
              )}
            </div>
          )}

          {/* Accessories */}
          {recommendations.accessories.length > 0 && (
            <div className={styles.section}>
              <h4>🎒 Accessories</h4>
              <ul className={styles.list}>
                {recommendations.accessories.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Footwear */}
          {recommendations.footwear.length > 0 && (
            <div className={styles.section}>
              <h4>👟 Footwear</h4>
              <ul className={styles.list}>
                {recommendations.footwear.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Tips */}
          {recommendations.tips.length > 0 && (
            <div className={styles.section}>
              <h4>💡 Tips</h4>
              <ul className={styles.list}>
                {recommendations.tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback */}
          {!feedbackGiven && (
            <div className={styles.feedback}>
              <p>Was this helpful?</p>
              <div className={styles.feedbackButtons}>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleFeedback("helpful")}
                  className={styles.helpfulButton}
                >
                  👍 Yes
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleFeedback("not_helpful")}
                  className={styles.notHelpfulButton}
                >
                  👎 No
                </Button>
              </div>
            </div>
          )}

          {feedbackGiven && (
            <div className={styles.thankYou}>
              ✅ Thank you for your feedback!
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FashionTips;
