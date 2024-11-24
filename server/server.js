// import { BskyAgent } from '@atproto/api';
// import 'dotenv/config';
// import fs from 'fs/promises';
// import path from 'path';

// const agent = new BskyAgent({
//   service: 'https://bsky.social',
// });

// const loginToBluesky = async () => {
//   try {
//     await agent.login({
//       identifier: process.env.BLUESKY_HANDLE,
//       password: process.env.BLUESKY_PASSWORD,
//     });
//     console.log('Logged in as:', process.env.BLUESKY_HANDLE);
//   } catch (error) {
//     console.error('Login failed:', error);
//     process.exit(1);
//   }
// };

// const savePostImages = async (images) => {
//   try {
//     for (const image of images) {
//       const timestamp = Date.now();
//       const imageRef = image.image.ref;
//       const mimeType = image.image.mimeType;
//       const extension = mimeType.split('/')[1]; // Get 'jpeg' from 'image/jpeg'
      
//       const filename = `image_${timestamp}_${imageRef.toString()}.${extension}`;
//       const filepath = path.join('./images', filename);

//       // Get the image data using the CID
//       const imageData = await agent.com.atproto.sync.getBlob({
//         did: agent.session.did,
//         cid: imageRef.toString()
//       });

//       // Save the image data to a file
//       await fs.writeFile(filepath, Buffer.from(await imageData.data.arrayBuffer()));
//       console.log(`Saved image: ${filename}`);
//     }
//   } catch (error) {
//     console.error('Error saving images:', error);
//   }
// };

// const replyToMention = async (mention) => {
//   try {
//     const response = await agent.post({
//       text: 'hi',
//       reply: {
//         root: {
//           uri: mention.uri,
//           cid: mention.cid,
//         },
//         parent: {
//           uri: mention.uri,
//           cid: mention.cid,
//         },
//       },
//     });
    
//     console.log('Successfully replied to mention');
//     return response;
//   } catch (error) {
//     console.error('Reply error:', error);
//     return null;
//   }
// };

// const checkMentions = async () => {
//   try {
//     const response = await agent.app.bsky.notification.listNotifications({ limit: 50 });
    
//     if (response.data.notifications.length === 0) {
//       return;
//     }

//     const mentions = response.data.notifications.filter(
//       (notif) => notif.reason === 'mention' && !notif.isRead
//     );

//     if (mentions.length > 0) {
//       for (const mention of mentions) {
//         console.log('New mention found:', mention.record.text);
        
//         // Check and save images from the mention
//         if (mention.record.embed?.$type === 'app.bsky.embed.images') {
//           await savePostImages(mention.record.embed.images);
//         }
        
//         // Reply with simple text
//         const reply = await replyToMention(mention);
        
//         if (reply) {
//           await agent.app.bsky.notification.updateSeen({ seenAt: new Date().toISOString() });
//           console.log('Marked as read');
//         }
//       }
//     }
//   } catch (error) {
//     console.error('Check mentions error:', error);
    
//     if (error.message?.includes('auth')) {
//       console.log('Attempting to re-login...');
//       await loginToBluesky();
//     }
//   }
// };

// const ensureImagesFolder = async () => {
//   try {
//     await fs.access('./images');
//   } catch {
//     console.log('Creating images folder...');
//     await fs.mkdir('./images');
//   }
// };

// const runBot = async () => {
//   await ensureImagesFolder();
//   await loginToBluesky();
//   console.log('Bot started! Checking mentions every 5 seconds...');

//   await checkMentions();
//   setInterval(checkMentions, 5000);
// };

// process.on('unhandledRejection', (error) => {
//   console.error('Unhandled rejection:', error);
// });

// runBot().catch((error) => {
//   console.error('Bot crashed:', error);
//   process.exit(1);
// });

import { AtpAgent } from '@atproto/api';
import 'dotenv/config';
import fs from 'fs/promises';
import path from 'path';
import sharp from 'sharp'; // For image processing and metadata stripping

const agent = new AtpAgent({
  service: 'https://bsky.social',
});

const MAX_IMAGE_SIZE = 10000000; // 1MB size limit

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

const processAndSaveImage = async (imageData, filename) => {
  try {
    // Process image with sharp to strip metadata and optimize
    const processedImage = await sharp(imageData)
      .withMetadata(false) // Strip EXIF metadata
      .jpeg({ quality: 80 }) // Convert to JPEG with reasonable quality
      .toBuffer();

    // Check file size
    if (processedImage.length > MAX_IMAGE_SIZE) {
      console.error(`Image too large (${processedImage.length} bytes), skipping: ${filename}`);
      return null;
    }

    // Save processed image
    const filepath = path.join('./images', filename);
    await fs.writeFile(filepath, processedImage);
    
    return {
      filepath,
      data: processedImage,
      size: processedImage.length
    };
  } catch (error) {
    console.error('Error processing image:', error);
    return null;
  }
};

const uploadBlob = async (imageBuffer, mimeType) => {
  try {
    const response = await agent.uploadBlob(imageBuffer, {
      encoding: mimeType,
    });

    return response.data.blob;
  } catch (error) {
    console.error('Error uploading blob:', error);
    return null;
  }
};

const savePostImages = async (embed) => {
  try {
    if (!embed || embed.$type !== 'app.bsky.embed.images' || !embed.images) {
      return;
    }

    for (const image of embed.images) {
        
      try {
        // Get the image data using the blob reference
        const imageData = await agent.com.atproto.sync.getBlob({
          did: agent.session.did,
          cid: image.image.ref.$link || image.image.ref.toString()
        });

        if (!imageData.data) {
          console.error('No image data received');
          continue;
        }

        // Create filename using CID and timestamp
        const timestamp = Date.now();
        const cid = image.image.ref.$link || image.image.ref.toString();
        const extension = image.image.mimeType.split('/')[1];
        const filename = `image_${timestamp}_${cid}.${extension}`;

        // Process and save the image
        const processedImage = await processAndSaveImage(
          Buffer.from(await imageData.data.arrayBuffer()),
          filename
        );

        if (processedImage) {
          console.log(`Saved image: ${filename}`);
          console.log(`Original alt text: ${image.alt || 'No alt text provided'}`);
        }

      } catch (error) {
        console.error('Error processing individual image:', error);
        continue;
      }
    }
  } catch (error) {
    console.error('Error in savePostImages:', error);
  }
};

const replyToMention = async (mention) => {
  try {
    const response = await agent.post({
      text: 'hi',
      reply: {
        root: {
          uri: mention.uri,
          cid: mention.cid,
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

const checkMentions = async () => {
  try {
    const response = await agent.app.bsky.notification.listNotifications({ limit: 50 });
    
    if (response.data.notifications.length === 0) {
      return;
    }

    const mentions = response.data.notifications.filter(
      (notif) => notif.reason === 'mention' && !notif.isRead
    );

    if (mentions.length > 0) {
      for (const mention of mentions) {
        console.log('New mention found:', mention.record.text);
        
        if (mention.record.embed) {
          await savePostImages(mention.record.embed);
        }
        
        const reply = await replyToMention(mention);
        
        if (reply) {
          await agent.app.bsky.notification.updateSeen({ seenAt: new Date().toISOString() });
          console.log('Marked as read');
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
  console.log('Bot started! Checking mentions every 5 seconds...');

  await checkMentions();
  setInterval(checkMentions, 5000);
};

process.on('unhandledRejection', (error) => {
  console.error('Unhandled rejection:', error);
});

runBot().catch((error) => {
  console.error('Bot crashed:', error);
  process.exit(1);
});