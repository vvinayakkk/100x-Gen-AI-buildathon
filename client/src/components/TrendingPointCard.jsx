import React from 'react';
import { motion } from 'framer-motion';

const TrendPointCard = ({ points, category }) => {
  const pointConfigurations = {
    stocks: [
      'key_market_trends',
      'potential_investment_opportunities', 
      'risk_assessment', 
      'sentiment_summary'
    ],
    financial_news: [
      'key_market_trends',
      'potential_investment_opportunities', 
      'risk_assessment', 
      'sentiment_summary'
    ],
    crypto: [
      'key_emerging_trends',
      'most_discussed_subtopics', 
      'potential_future_directions', 
      'sentiment_and_engagement_summary'
    ],
    tech: [
      'key_emerging_trends',
      'most_discussed_subtopics', 
      'potential_future_directions', 
      'sentiment_and_engagement_summary'
    ],
    finance: [
      'key_emerging_trends',
      'most_discussed_subtopics', 
      'potential_future_directions', 
      'sentiment_and_engagement_summary'
    ],
    entertainment: [
      'key_emerging_trends',
      'most_discussed_subtopics', 
      'potential_future_directions', 
      'sentiment_and_engagement_summary'
    ]
  };

  const categoryTitles = {
    key_market_trends: 'Market Pulse',
    potential_investment_opportunities: 'Investment Insights',
    risk_assessment: 'Risk Landscape',
    sentiment_summary: 'Sentiment Overview',
    key_emerging_trends: 'Emerging Horizons',
    most_discussed_subtopics: 'Topic Spotlight',
    potential_future_directions: 'Future Forecast',
    sentiment_and_engagement_summary: 'Community Pulse'
  };

  const categoryIcons = {
    key_market_trends: '📈',
    potential_investment_opportunities: '💡',
    risk_assessment: '⚠️',
    sentiment_summary: '📊',
    key_emerging_trends: '🌟',
    most_discussed_subtopics: '💬',
    potential_future_directions: '🔮',
    sentiment_and_engagement_summary: '🌐'
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {pointConfigurations[category]?.map((configKey, index) => {
        const point = points?.[configKey] || 'Analyzing data...';
        const title = categoryTitles[configKey];
        const icon = categoryIcons[configKey];
        
        return (
          <motion.div
            key={configKey}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              delay: index * 0.1, 
              type: 'spring', 
              stiffness: 100 
            }}
            className="bg-gradient-to-br from-gray-800 to-gray-900 
              rounded-2xl p-5 border border-gray-700 
              shadow-lg hover:shadow-2xl 
              transform hover:-translate-y-2 
              transition-all duration-300 
              group"
          >
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-3">{icon}</span>
              <h3 className="text-sm font-semibold text-blue-300 
                group-hover:text-blue-200 transition-colors">
                {title}
              </h3>
            </div>
            <p className="text-xs text-gray-400 
              line-clamp-3 h-12 
              group-hover:text-gray-200 
              transition-colors">
              {point}
            </p>
            <div className="mt-3 h-0.5 w-full 
              bg-gradient-to-r from-transparent 
              via-blue-500 to-transparent 
              opacity-0 group-hover:opacity-100 
              transition-opacity duration-300">
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default TrendPointCard;