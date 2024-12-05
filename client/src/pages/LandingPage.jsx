import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnalysisService } from '../services/api-service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AlertTriangle, TrendingUp, Star, BarChart, Activity, 
  ChevronDown, TrendingUp as TrendIcon, 
  AlertOctagon, 
  Target, 
  BarChartHorizontal 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart as RechartsBarChart, 
  Bar,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';


const TrendPointCard = ({ points, category }) => {
  const pointConfigurations = {
    stocks: [
      { title: 'Key Market Trends', icon: TrendIcon },
      { title: 'Potential Investment Opportunities', icon: Target },
      { title: 'Risk Assessment', icon: AlertOctagon },
      { title: 'Sentiment Summary', icon: BarChartHorizontal }
    ],
    financial_news: [
      { title: 'Key Market Trends', icon: TrendIcon },
      { title: 'Potential Investment Opportunities', icon: Target },
      { title: 'Risk Assessment', icon: AlertOctagon },
      { title: 'Sentiment Summary', icon: BarChartHorizontal }
    ],
    crypto: [
      { title: 'Key Emerging Trends', icon: TrendIcon },
      { title: 'Most Discussed Subtopics', icon: BarChartHorizontal },
      { title: 'Potential Future Directions', icon: Target },
      { title: 'Sentiment and Engagement Summary', icon: AlertOctagon }
    ]
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {pointConfigurations[category]?.map((config, index) => {
        const Icon = config.icon;
        const point = points?.[config.title.toLowerCase().replace(/\s+/g, '_')] || 'No data available';
        
        return (
          <motion.div
            key={config.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-gray-800 rounded-xl p-4 border border-gray-700 shadow-lg hover:bg-gray-700/50 transition-all group"
          >
            <div className="flex items-center mb-3">
              <Icon className="w-6 h-6 mr-3 text-blue-400 group-hover:text-blue-300 transition-colors" />
              <h3 className="text-sm font-semibold text-blue-300 group-hover:text-blue-200">
                {config.title}
              </h3>
            </div>
            <p className="text-xs text-gray-300 line-clamp-3">{point}</p>
          </motion.div>
        );
      })}
    </div>
  );
};

// Loading overlay component
const LoadingOverlay = () => (
  <div className="absolute inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50 rounded-lg">
    <div className="flex flex-col items-center gap-2">
      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-sm text-blue-400">Loading analysis...</p>
    </div>
  </div>
);

// Enhanced skeleton with wave effect
const AnalysisCardSkeleton = () => (
  <div className="space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="relative overflow-hidden">
        <div className="h-4 bg-gray-700 rounded animate-pulse">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-wave" />
        </div>
      </div>
    ))}
  </div>
);

const TopicClustersVisualization = ({ clusters }) => {
  if (!clusters?.clusters) return null;

  const clusterCounts = clusters.clusters.reduce((acc, cluster) => {
    acc[`Cluster ${cluster}`] = (acc[`Cluster ${cluster}`] || 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(clusterCounts).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer>
        <RechartsBarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey="name" className="text-xs" />
          <YAxis className="text-xs" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(17, 24, 39, 0.8)',
              border: 'none',
              borderRadius: '8px',
              color: 'white'
            }}
          />
          <Bar 
            dataKey="value" 
            fill="#8884d8"
            radius={[4, 4, 0, 0]}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

const ClusterScatterPlot = ({ centroids, clusters }) => {
  if (!centroids || !clusters) return null;

  // Transform centroids data for visualization
  const centroidData = centroids.map((centroid, idx) => ({
    x: centroid[0] * 100,
    y: centroid[1] * 100,
    z: 20, // Size for centroids
    cluster: `Centroid ${idx}`,
    isCentroid: true
  }));

  // Transform cluster points
  const clusterPoints = clusters.map((cluster, idx) => ({
    x: Math.random() * 100, // You would use actual coordinates from your data
    y: Math.random() * 100,
    z: 10, // Size for regular points
    cluster: `Cluster ${cluster}`,
    isCentroid: false
  }));

  const allData = [...centroidData, ...clusterPoints];

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis type="number" dataKey="x" name="x" unit="" />
          <YAxis type="number" dataKey="y" name="y" unit="" />
          <ZAxis type="number" dataKey="z" range={[100, 200]} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(17, 24, 39, 0.8)',
              border: 'none',
              borderRadius: '8px',
              color: 'white'
            }}
          />
          <Scatter 
            data={allData} 
            fill={(entry) => entry.isCentroid ? '#ff4444' : '#8884d8'}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

const SentimentTrend = ({ sentiments }) => {
  if (!sentiments?.top_positive || !sentiments?.top_negative) return null;

  const data = [];
  
  // Combine positive and negative sentiments
  sentiments.top_positive.forEach((item, index) => {
    data.push({
      name: `Point ${index + 1}`,
      positive: item.confidence,
      negative: sentiments.top_negative[index]?.confidence || 0
    });
  });

  return (
    <div className="h-40 w-full mt-4">
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey="name" className="text-xs" />
          <YAxis domain={[0, 1]} className="text-xs" />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(17, 24, 39, 0.8)',
              border: 'none',
              borderRadius: '8px',
              color: 'white'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="positive" 
            stroke="#4ade80" 
            strokeWidth={2}
            dot={{ fill: '#4ade80' }}
            name="Positive"
          />
          <Line 
            type="monotone" 
            dataKey="negative" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={{ fill: '#ef4444' }}
            name="Negative"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const HomePage = () => {
  const [activeCategory, setActiveCategory] = useState('stocks');
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isTrendCategory, setIsTrendCategory] = useState(false);

  const mainCategories = [
    { id: 'stocks', icon: <Activity className="w-4 h-4" />, label: 'Stocks' },
    { id: 'news', icon: <AlertTriangle className="w-4 h-4" />, label: 'News' },
    { id: 'crypto', icon: <TrendingUp className="w-4 h-4" />, label: 'Crypto' },
  ];

  const trendCategories = [
    { id: 'tech', label: 'Technology' },
    { id: 'finance', label: 'Finance' },
    { id: 'entertainment', label: 'Entertainment' },
  ];

  useEffect(() => {
    let isMounted = true;
    
    const fetchAnalysis = async () => {
      setIsLoading(true);
      setAnalysisData(null); // Clear existing data before new fetch
      
      try {
        let data;
        
        // Select appropriate service method based on category and type
        if (isTrendCategory) {
          switch (activeCategory) {
            case 'tech':
              data = await AnalysisService.getTechTrends();
              break;
            case 'finance':
              data = await AnalysisService.getFinanceTrends();
              break;
            case 'entertainment':
              data = await AnalysisService.getEntertainmentTrends();
              break;
            default:
              throw new Error('Invalid trend category');
          }
        } else {
          switch (activeCategory) {
            case 'stocks':
              data = await AnalysisService.getStockAnalysis();
              break;
            case 'news':
              data = await AnalysisService.getNewsAnalysis();
              break;
            case 'crypto':
              data = await AnalysisService.getCryptoAnalysis();
              break;
            default:
              throw new Error('Invalid category');
          }
        }
        
        if (isMounted) {
          setAnalysisData(data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          console.error('Error fetching analysis:', err);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchAnalysis();

    return () => {
      isMounted = false;
    };
  }, [activeCategory, isTrendCategory]);

  const handleCategoryChange = (category, isTrend = false) => {
    setActiveCategory(category);
    setIsTrendCategory(isTrend);
  };
  const renderContent = (section) => {
    if (isLoading) {
      return <AnalysisCardSkeleton />;
    }

    switch (section) {
      case 'sentiment':
      return (
        <>
          <div className="text-sm text-gray-300">
            Total Analyzed: {analysisData?.sentiment_analysis?.total_analyzed || 0}
          </div>
          <SentimentTrend sentiments={analysisData?.sentiment_analysis} />
          <div className="space-y-4">
            <div>
              <h4 className="text-green-400 font-medium mb-2">Top Positive</h4>
              {analysisData?.sentiment_analysis?.top_positive?.map((item, index) => (
                <motion.div
                  key={`pos-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="mt-2 p-2 bg-gray-700 rounded-lg text-sm"
                >
                  <div className="font-medium text-green-400">
                    {item.text.substring(0, 50)}...
                  </div>
                  <div className="text-xs text-gray-400">
                    Confidence: {(item.confidence * 100).toFixed(1)}%
                  </div>
                </motion.div>
              ))}
            </div>
            <div>
              <h4 className="text-red-400 font-medium mb-2">Top Negative</h4>
              {analysisData?.sentiment_analysis?.top_negative?.map((item, index) => (
                <motion.div
                  key={`neg-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="mt-2 p-2 bg-gray-700 rounded-lg text-sm"
                >
                  <div className="font-medium text-red-400">
                    {item.text.substring(0, 50)}...
                  </div>
                  <div className="text-xs text-gray-400">
                    Confidence: {(item.confidence * 100).toFixed(1)}%
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </>
      );
    case 'clusters':
      return (
        <>
          <ClusterScatterPlot 
            centroids={analysisData?.topic_clusters?.centroids}
            clusters={analysisData?.topic_clusters?.clusters}
          />
          <TopicClustersVisualization clusters={analysisData?.topic_clusters} />
          <div className="mt-4 space-y-2">
            {analysisData?.topic_clusters?.clusters?.slice(0, 5).map((cluster, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center text-sm text-gray-300"
              >
                <div className="w-2 h-2 rounded-full bg-yellow-400 mr-2" />
                Cluster {index + 1}: {cluster}
              </motion.div>
            ))}
          </div>
        </>
      );
      
  // Check if ai_insights exists and is not empty
  case 'insights':
    return (
      <div className="space-y-4">
        {!analysisData?.ai_insights ? (
          <div className="text-gray-400 text-sm flex items-center justify-center h-full">
            No insights available for this category
          </div>
        ) : (
          <div className="prose prose-sm prose-invert">
            {analysisData.ai_insights.split('\n\n').map((paragraph, index) => (
              <motion.p
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-sm text-gray-300 mb-3"
              >
                {paragraph}
              </motion.p>
            ))}
          </div>
        )}
      </div>
    );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto space-y-8"
      >
        <div className="flex justify-center mb-8 gap-2 flex-wrap">
          {mainCategories.map(({ id, icon, label }) => (
            <Button
              key={id}
              variant={activeCategory === id && !isTrendCategory ? "default" : "outline"}
              className={`
                px-6 py-2 rounded-full transition-all duration-300
                ${activeCategory === id && !isTrendCategory ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-700'}
              `}
              onClick={() => handleCategoryChange(id, false)}
            >
              <span className="mr-2">{icon}</span>
              {label}
            </Button>
          ))}
  
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant={isTrendCategory ? "default" : "outline"}
                className={`
                  px-6 py-2 rounded-full transition-all duration-300
                  ${isTrendCategory ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-700'}
                `}
              >
                <BarChart className="w-4 h-4 mr-2" />
                Trends
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-gray-700">
              {trendCategories.map(({ id, label }) => (
                <DropdownMenuItem
                  key={id}
                  className="text-white hover:bg-gray-700 cursor-pointer"
                  onClick={() => handleCategoryChange(id, true)}
                >
                  {label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
  
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
  
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-2xl"
          >
            <h2 className="text-2xl font-bold mb-6 text-blue-300">
              Trend Analysis Overview
            </h2>
            <TrendPointCard 
              points={analysisData?.trend_points} 
              category={activeCategory === 'news' ? 'financial_news' : activeCategory} 
            />
          </motion.div>
          
          <AnimatePresence mode="wait">
            {['sentiment', 'clusters'].map((section, index) => (
              <motion.div
                key={`${section}-${activeCategory}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="relative"
              >
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-blue-400">
                      {section === 'sentiment' && <TrendingUp className="mr-2" />}
                      {section === 'clusters' && <BarChart className="mr-2" />}
                      {section.charAt(0).toUpperCase() + section.slice(1)} Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="relative min-h-[300px]">
                    {isLoading && <LoadingOverlay />}
                    {renderContent(section)}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default HomePage;