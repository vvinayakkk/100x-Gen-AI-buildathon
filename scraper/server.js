import { BskyAgent } from '@atproto/api';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import cron from 'node-cron';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

class BlueSkyTrendsAnalyzer {
  constructor() {
    this.agent = new BskyAgent({ 
      service: 'https://bsky.social',
      persistSession: this.saveSession.bind(this)
    });

    this.configPath = path.join(__dirname, 'config.json');
    this.dataStorePath = path.join(__dirname, 'data_store');
    
    // Control variables for tracking results
    this.financeResults = [];
    this.web3Results = [];
  }

  async authenticate() {
    try {
      await this.agent.login({
        identifier: process.env.BLUESKY_HANDLE,
        password: process.env.BLUESKY_PASSWORD
      });
      console.log('Authenticated successfully');
    } catch (error) {
      console.error('Authentication failed:', error);
      process.exit(1);
    }
  }

  async crawlFinanceContent() {
    const searchTerms = ['crypto', 'stocks', 'finance', 'investment'];
    const allResults = [];

    for (const term of searchTerms) {
      try {
        const searchResults = await this.agent.app.bsky.feed.searchPosts({
          q: term,
          limit: 50
        });

        const filteredResults = searchResults.data.posts.filter(this.isRelevantFinancePost);
        allResults.push(...filteredResults);
        
        console.log(`Finance crawl for "${term}": ${filteredResults.length} posts`);
      } catch (error) {
        console.error(`Finance search error for ${term}:`, error);
      }
    }

    // Update results and save
    this.financeResults = allResults;
    await this.saveData(allResults, 'finance');
    return allResults;
  }

  async crawlWeb3Content() {
    const searchTerms = ['blockchain', 'web3', 'cryptocurrency', 'defi'];
    const allResults = [];

    for (const term of searchTerms) {
      try {
        const searchResults = await this.agent.app.bsky.feed.searchPosts({
          q: term,
          limit: 50
        });

        const filteredResults = searchResults.data.posts.filter(this.isRelevantWeb3Post);
        allResults.push(...filteredResults);
        
        console.log(`Web3 crawl for "${term}": ${filteredResults.length} posts`);
      } catch (error) {
        console.error(`Web3 search error for ${term}:`, error);
      }
    }

    // Update results and save
    this.web3Results = allResults;
    await this.saveData(allResults, 'web3');
    return allResults;
  }

  getFinanceResults() {
    return {
      count: this.financeResults.length,
      results: this.financeResults
    };
  }

  getWeb3Results() {
    return {
      count: this.web3Results.length,
      results: this.web3Results
    };
  }

  isRelevantFinancePost(post) {
    const keywords = ['stocks', 'market', 'investment', 'trading', 'portfolio'];
    const text = post.record.text.toLowerCase();
    return keywords.some(keyword => text.includes(keyword));
  }

  isRelevantWeb3Post(post) {
    const keywords = ['blockchain', 'ethereum', 'bitcoin', 'defi', 'nft'];
    const text = post.record.text.toLowerCase();
    return keywords.some(keyword => text.includes(keyword));
  }

  async saveData(data, type) {
    try {
      await this.ensureDirectoryExists(this.dataStorePath);
      const filePath = path.join(this.dataStorePath, `${type}_${Date.now()}.json`);
      await fs.writeFile(filePath, JSON.stringify(data, null, 2));
      console.log(`Saved ${data.length} ${type} posts to ${filePath}`);
    } catch (error) {
      console.error(`Error saving ${type} data:`, error);
    }
  }

  async ensureDirectoryExists(dirPath) {
    await fs.mkdir(dirPath, { recursive: true });
  }

  async saveSession(session) {
    await fs.writeFile(this.configPath, JSON.stringify(session, null, 2));
  }

  async run() {
    await this.authenticate();
    
    // Crawl every 2 minutes
    cron.schedule('*/2 * * * *', () => {
      console.log('Starting finance content crawl');
      this.crawlFinanceContent();
    });

    cron.schedule('1,3,5 * * * *', () => {
      console.log('Starting Web3 content crawl');
      this.crawlWeb3Content();
    });

    // Keep the process running
    console.log('Trends analyzer started. Crawling content every 2 minutes.');
  }
}

const analyzer = new BlueSkyTrendsAnalyzer();
analyzer.run().catch(console.error);