import { AtpAgent } from '@atproto/api';
import 'dotenv/config';
import fs from 'fs/promises';
import path from 'path';
import sharp from 'sharp';
import axios from 'axios';

const agent = new AtpAgent({
  service: 'https://bsky.social',
});

const MAX_IMAGE_SIZE = 10000000;
const loginToBluesky = async () => {
  try {
    await agent.login({
      identifier: process.env.BLUESKY_HANDLE,
      password: process.env.BLUESKY_PASSWORD,
    });
    console.log('Logged in as:', process.env.BLUESKY_HANDLE);
  } catch (error) {
    console.error('Login failed:', error);
    process.exit(1);
  }
};

// ... (keeping all the image processing functions the same)

const replyToMention = async (mention, rootPost, replyText) => {
  try {
    const response = await agent.post({
      text: replyText,
      reply: {
        root: {
          uri: rootPost?.uri || mention.uri,
          cid: rootPost?.cid || mention.cid,
        },
        parent: {
          uri: mention.uri,
          cid: mention.cid,
        },
      },
    });
    
    console.log('Successfully replied to mention');
    return response;
  } catch (error) {
    console.error('Reply error:', error);
    return null;
  }
};


const splitContentIntoChunks = (content, maxLength = 299) => {
  const sentences = content.match(/[^.!?]+[.!?]+/g) || [];
  const chunks = [];
  let currentChunk = '';

  for (const sentence of sentences) {
    // Check if adding this sentence would exceed maxLength
    if ((currentChunk + sentence).length <= maxLength) {
      currentChunk += sentence;
    } else {
      // If current chunk is not empty, push it to chunks
      if (currentChunk) {
        chunks.push(currentChunk.trim());
      }
      // Start new chunk with current sentence if it fits
      currentChunk = sentence.length <= maxLength ? sentence : sentence.substring(0, maxLength);
    }
  }

  // Push the last chunk if not empty
  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }

  return chunks.reverse();
};

const processAndUploadImage = async (imageUrl) => {
  try {
    // Download the image
    const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const buffer = Buffer.from(response.data);
    
    // Process image with sharp
    const processedImage = await sharp(buffer)
      .resize(1000, 1000, { 
        fit: 'inside',
        withoutEnlargement: true 
      })
      .toBuffer();
      
    // Check if image size is within limits
    if (processedImage.length > MAX_IMAGE_SIZE) {
      throw new Error('Processed image exceeds maximum size limit');
    }
    
    // Upload to Bluesky
    const uploadResponse = await agent.uploadBlob(processedImage, {
      encoding: 'image/jpeg'
    });
    
    return {
      $type: 'app.bsky.embed.images',
      images: [{
        alt: 'Default response image',
        image: uploadResponse.data.blob
      }]
    };
  } catch (error) {
    console.error('Error processing image:', error);
    return null;
  }
};

const processMention = async (mention, rootPost) => {
  try {
    const user_text = mention.record.text.split('bsky.social')[1].trim();
    const root_text = rootPost ? rootPost.text : '';

    console.log(`User text: ${user_text}`);
    console.log(`Tweet text: ${root_text}`);
    
    const data = {
      userCommand: user_text,
      originalTweet: root_text
    };
    
    const config = {
      method: 'post',
      url: `${process.env.API_MIDDLEWARE}/process-mention`,
      headers: { 
        'Content-Type': 'application/json'
      },
      data: data
    };
    
    const response = await axios(config);
    
    if (response.data.category === "Impersonation Agent") {
      const ai_response = String(response.data.result.response);
      var res_arr = splitContentIntoChunks(ai_response);
      console.log('AI Response:', res_arr);
      for(const res of res_arr){
        await replyToMention(mention, rootPost,res);
      }
    }
    else if (response.data.category === "Viral Thread Generator" ){
      console.log(response.data.result);
      var ai_texts = response.data.result.slice(0,5).reverse();
      console.log('AI Response:', ai_texts);
      for(const ai_text of ai_texts){
        await replyToMention(mention, rootPost, String(ai_text.content).substring(0,299));
      }
    }
    else if (response.data.category === "Fact-Checker Agent" ){
      var ai_response = response.data.result.analyses.wikipedia.articles;
      var res_arr = splitContentIntoChunks(ai_response[0].content);
      console.log('AI Response:', res_arr);
      for(const res of res_arr){
        await replyToMention(mention, rootPost,res);
      }
      // return await replyToMention(mention, rootPost, String(ai_response[0].content).substring(0,299));
    }
    else if (response.data.category === "Sentiment Analyzer" ){
      var ai_response = response.data.result.analysis.emotion_profile.dominant_emotion;
      var detailed_emo_arr = response.data.result.analysis.emotion_profile.detailed_emotions;
      var data_str = ""
      Object.keys(detailed_emo_arr).forEach(key => {
        var temp = Math.floor((Number(detailed_emo_arr[key]) *100));
        data_str += temp+  ","
      });
      console.log(data_str);
      var url = process.env.CHART + data_str;
      const imageEmbed = await processAndUploadImage(url);
      if (imageEmbed) {    
        const response = await agent.post({
          text: `By my analysis this tweet is : ${ai_response}`,
          embed: imageEmbed,
          reply: {
            root: {
              uri: rootPost?.uri || mention.uri,
              cid: rootPost?.cid || mention.cid,
            },
            parent: {
              uri: mention.uri,
              cid: mention.cid,
            },
          },
        });
        console.log('Successfully posted image response');
      }
    }
    else if(response.data.category === "Meme Creator"){
      var url = response.data.result.url;
      const imageEmbed = await processAndUploadImage(url);
      if (imageEmbed) {    
          const response = await agent.post({
            text: "Here's a response for you!",
            embed: imageEmbed,
            reply: {
              root: {
                uri: rootPost?.uri || mention.uri,
                cid: rootPost?.cid || mention.cid,
              },
              parent: {
                uri: mention.uri,
                cid: mention.cid,
              },
            },
          });
          console.log('Successfully posted image response');
    }
    
  }
  else if (response.data.category === "Generic" ){
    var ai_texts = response.data.result.result;
    var res_arr = splitContentIntoChunks(ai_texts);
    console.log('AI Response:', res_arr);
    for(const res of res_arr){
      await replyToMention(mention, rootPost,res);
    }
  }
    return true;
  } catch (error) {
    console.error('Error processing mention:', error);
    return null;
  }
};

const getRootPost = async (uri) => {
  try {
    const response = await agent.api.app.bsky.feed.getPostThread({
      uri: uri,
      depth: 0,
    });
    
    if (response.data.thread?.post) {
      const post = response.data.thread.post;
      return {
        text: post.record.text,
        uri: post.uri,
        cid: post.cid,
        embed: post.record.embed
      };
    }
    return null;
  } catch (error) {
    console.error('Error getting root post:', error);
    return null;
  }
};

const checkMentions = async () => {
  try {
    const response = await agent.app.bsky.notification.listNotifications({ limit: 50 });
    
    if (!response.data.notifications.length) {
      return;
    }

    const mentions = response.data.notifications.filter(
      (notif) => notif.reason === 'mention' && !notif.isRead
    );

    if (mentions.length > 0) {
      console.log(`Processing ${mentions.length} new mentions...`);
      
      for (const mention of mentions) {
        console.log('Processing mention:', mention.record.text);
        
        // Get the root post
        const rootPost = await getRootPost(mention.record.reply?.parent?.uri);
        
        // Process the mention and get response
        const reply = await processMention(mention, rootPost);
        
        if (reply) {
          // Mark this specific notification as read
          await agent.app.bsky.notification.updateSeen({
            seenAt: new Date().toISOString()
          });
          console.log('Marked notification as read');
        }
      }
    }
  } catch (error) {
    console.error('Check mentions error:', error);
    
    if (error.message?.includes('auth')) {
      console.log('Attempting to re-login...');
      await loginToBluesky();
    }
  }
};

const ensureImagesFolder = async () => {
  try {
    await fs.access('./images');
  } catch {
    console.log('Creating images folder...');
    await fs.mkdir('./images');
  }
};

const runBot = async () => {
  await ensureImagesFolder();
  await loginToBluesky();
  console.log('Bot started! Checking mentions every 30 seconds...');

  // Initial check
  await checkMentions();
  
  // Set up interval with longer delay to avoid rate limits
  setInterval(checkMentions, 120000);
};

process.on('unhandledRejection', (error) => {
  console.error('Unhandled rejection:', error);
});

runBot().catch((error) => {
  console.error('Bot crashed:', error);
  process.exit(1);
});