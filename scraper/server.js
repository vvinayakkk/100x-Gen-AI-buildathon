import { BskyAgent } from '@atproto/api';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class BlueskyFinancialCrawler {
  constructor() {
    dotenv.config();
    this.agent = new BskyAgent({ service: 'https://bsky.social' });
    
    this.dataStorePath = path.join(__dirname, 'data');
    this.categories = {
      stockUpdates: path.join(this.dataStorePath, 'stocks', 'latest.json'),
      financialNews: path.join(this.dataStorePath, 'financial_news', 'latest.json'),
      investmentInsights: path.join(this.dataStorePath, 'investment_insights', 'latest.json')
    };
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

  async crawlFinancialContent() {
    const searchTerms = [
      'stocks', 'finance', 'investment', 
      'market', 'trading', 'portfolio'
    ];

    const allPosts = [];

    for (const term of searchTerms) {
      try {
        const searchResults = await this.agent.app.bsky.feed.searchPosts({
          q: term,
          limit: 100
        });

        const filteredPosts = searchResults.data.posts
          .map(post => ({
            text: post.record.text,
            createdAt: post.record.createdAt
          }));

        allPosts.push(...filteredPosts);
      } catch (error) {
        console.error(`Search error for ${term}:`, error);
      }
    }

    await this.categorizeAndSavePosts(allPosts);
  }

  async categorizeAndSavePosts(posts) {
    // Ensure all category directories exist
    for (const categoryDir of Object.values(this.categories).map(path.dirname)) {
      await fs.mkdir(categoryDir, { recursive: true });
    }

    const categorizedPosts = {
      stockUpdates: posts.filter(post => 
        /\$|stock|ticker|share price|trading/i.test(post.text)
      ),
      financialNews: posts.filter(post => 
        /market|economy|report|financial news/i.test(post.text)
      ),
      investmentInsights: posts.filter(post => 
        /advice|insight|recommendation|portfolio|investment strategy/i.test(post.text)
      )
    };

    for (const [category, categoryPosts] of Object.entries(categorizedPosts)) {
      await fs.writeFile(
        this.categories[category], 
        JSON.stringify(categoryPosts, null, 2)
      );

      console.log(`Saved ${categoryPosts.length} ${category} posts`);
    }
  }

  async startCrawling() {
    await this.authenticate();
    
    // Initial crawl
    await this.crawlFinancialContent();

    // Set up periodic crawling every 5 minutes
    setInterval(async () => {
      try {
        await this.crawlFinancialContent();
      } catch (error) {
        console.error('Periodic crawl error:', error);
      }
    }, 5 * 60 * 1000); // 5 minutes
  }
}

const crawler = new BlueskyFinancialCrawler();
crawler.startCrawling().catch(console.error);