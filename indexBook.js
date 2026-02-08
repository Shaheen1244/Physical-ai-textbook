/**
 * Book Content Indexing Script
 *
 * This script scans all markdown files inside the /docs directory,
 * splits content into meaningful chunks, generates embeddings for each chunk,
 * and upserts all embeddings into Qdrant collection named "book".
 *
 * Usage: node scripts/indexBook.js
 */

const fs = require('fs').promises;
const path = require('path');
const { Configuration, OpenAIApi } = require('openai');
const { QdrantClient } = require('@qdrant/js-client-rest');

// Load environment variables
require('dotenv').config({ path: '.env.local' });

// Configuration validation
const requiredEnvVars = ['QDRANT_URL', 'QDRANT_API_KEY', 'QDRANT_COLLECTION', 'OPENAI_API_KEY'];
const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0) {
    console.error('❌ Missing required environment variables:', missingEnvVars);
    console.error('Please ensure .env.local contains all required variables');
    process.exit(1);
}

const QDRANT_URL = process.env.QDRANT_URL;
const QDRANT_API_KEY = process.env.QDRANT_API_KEY;
const QDRANT_COLLECTION = process.env.QDRANT_COLLECTION || 'book';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// Initialize clients
const openai = new OpenAIApi(new Configuration({ apiKey: OPENAI_API_KEY }));
const qdrant = new QdrantClient({
    url: QDRANT_URL,
    apiKey: QDRANT_API_KEY,
});

/**
 * Read all markdown files from the docs directory
 */
async function readMarkdownFiles(docsPath = './docs') {
    console.log(`🔍 Scanning markdown files in ${docsPath}...`);

    const files = [];
    const dirents = await fs.readdir(docsPath, { withFileTypes: true });

    for (const dirent of dirents) {
        const fullPath = path.join(docsPath, dirent.name);

        if (dirent.isDirectory()) {
            // Recursively read subdirectories
            const subFiles = await readMarkdownFiles(fullPath);
            files.push(...subFiles);
        } else if (dirent.isFile() && path.extname(dirent.name) === '.md') {
            // Read markdown file
            const content = await fs.readFile(fullPath, 'utf8');
            files.push({
                filename: dirent.name,
                relativePath: path.relative('./docs', fullPath),
                fullPath: fullPath,
                content: content
            });
            console.log(`📄 Read file: ${fullPath}`);
        }
    }

    return files;
}

/**
 * Split markdown content into chunks by sections (headings)
 */
function chunkMarkdownContent(relativePath, content) {
    console.log(`✂️  Chunking content for: ${relativePath}`);

    // Split by markdown headings (##, ###, etc.) to maintain context
    const headingRegex = /^(#{2,6})\s+(.+)$/gm;
    const chunks = [];
    let lastIndex = 0;
    let match;

    // First, try to split by headings
    while ((match = headingRegex.exec(content)) !== null) {
        if (match.index > lastIndex) {
            // Add content before this heading as a chunk
            const chunkContent = content.substring(lastIndex, match.index).trim();
            if (chunkContent) {
                chunks.push({
                    content: chunkContent,
                    metadata: {
                        source_file: relativePath,
                        heading: '',
                        chunk_index: chunks.length,
                        collection: QDRANT_COLLECTION
                    }
                });
            }
        }

        // Start a new chunk from this heading
        lastIndex = match.index;
    }

    // Add the remaining content after the last heading
    if (lastIndex < content.length) {
        const chunkContent = content.substring(lastIndex).trim();
        if (chunkContent) {
            chunks.push({
                content: chunkContent,
                metadata: {
                    source_file: relativePath,
                    heading: '',
                    chunk_index: chunks.length,
                    collection: QDRANT_COLLECTION
                }
            });
        }
    }

    // If no headings were found, fall back to character-based splitting
    if (chunks.length === 0) {
        const chunkSize = 1000;
        const chunkOverlap = 200;

        for (let i = 0; i < content.length; i += chunkSize - chunkOverlap) {
            const chunk = content.slice(i, i + chunkSize);
            chunks.push({
                content: chunk,
                metadata: {
                    source_file: relativePath,
                    heading: 'General Content',
                    chunk_index: i / (chunkSize - chunkOverlap),
                    collection: QDRANT_COLLECTION
                }
            });
        }
    }

    // Further refine chunks to ensure they're not too large
    const refinedChunks = [];
    for (const chunk of chunks) {
        if (chunk.content.length > 1500) {
            // Split large chunks further
            const subChunks = splitLargeChunk(chunk.content, chunk.metadata.source_file);
            refinedChunks.push(...subChunks);
        } else {
            refinedChunks.push(chunk);
        }
    }

    return refinedChunks;
}

/**
 * Split large chunks into smaller ones
 */
function splitLargeChunk(content, sourceFile) {
    const chunkSize = 1000;
    const chunkOverlap = 200;
    const chunks = [];

    for (let i = 0; i < content.length; i += chunkSize - chunkOverlap) {
        const chunk = content.slice(i, i + chunkSize);
        chunks.push({
            content: chunk.trim(),
            metadata: {
                source_file: sourceFile,
                heading: 'Split Content',
                chunk_index: i / (chunkSize - chunkOverlap),
                collection: QDRANT_COLLECTION
            }
        });
    }

    return chunks;
}

/**
 * Generate embeddings for text chunks using OpenAI
 */
async function generateEmbeddings(texts) {
    console.log(`🧮 Generating embeddings for ${texts.length} chunks...`);

    try {
        const response = await openai.createEmbedding({
            model: 'text-embedding-ada-002',
            input: texts
        });

        return response.data.data.map(item => item.embedding);
    } catch (error) {
        console.error('❌ Error generating embeddings:', error.message);
        throw error;
    }
}

/**
 * Ensure Qdrant collection exists
 */
async function ensureCollection() {
    console.log(`📦 Ensuring Qdrant collection "${QDRANT_COLLECTION}" exists...`);

    try {
        // Try to get collection info to see if it exists
        await qdrant.getCollection(QDRANT_COLLECTION);
        console.log(`✅ Collection "${QDRANT_COLLECTION}" already exists`);
    } catch (error) {
        // Handle different types of errors
        if (error.status === 404) {
            // Collection doesn't exist, create it
            console.log(`🆕 Creating collection "${QDRANT_COLLECTION}"...`);

            await qdrant.createCollection(QDRANT_COLLECTION, {
                vectors: {
                    size: 1536, // OpenAI embedding size
                    distance: 'Cosine'
                }
            });

            console.log(`✅ Collection "${QDRANT_COLLECTION}" created successfully`);
        } else {
            // Network error or other issue - provide more detailed info
            console.warn(`⚠️  Warning: Cannot connect to Qdrant at ${QDRANT_URL}`);
            console.warn(`   Error: ${error.message}`);
            console.warn(`   Please ensure Qdrant is running and accessible`);
            console.warn(`   This could be because:`);
            console.warn(`   - Qdrant service is not running`);
            console.warn(`   - Network connectivity issues`);
            console.warn(`   - Incorrect URL or API key in .env.local`);
            console.warn(`   - Firewall blocking the connection`);

            // For now, throw the error to stop execution as connectivity is critical for the main purpose
            throw error;
        }
    }
}

/**
 * Index book content to Qdrant
 */
async function indexBooks() {
    console.log('📚 Starting book indexing process...\n');

    // Read all markdown files
    const markdownFiles = await readMarkdownFiles();

    if (markdownFiles.length === 0) {
        console.warn('⚠️  No markdown files found in docs directory');
        return {
            status: 'no_files_found',
            message: 'No markdown files found in docs directory',
            indexed_files: 0,
            total_chunks: 0
        };
    }

    console.log(`\n✅ Found ${markdownFiles.length} markdown files\n`);

    // Prepare all chunks
    let allChunks = [];
    let totalProcessedFiles = 0;

    for (const file of markdownFiles) {
        console.log(`\n📝 Processing: ${file.relativePath}`);

        const chunks = chunkMarkdownContent(file.relativePath, file.content);
        console.log(`   → Created ${chunks.length} chunks`);

        allChunks.push(...chunks);
        totalProcessedFiles++;
    }

    console.log(`\n📊 Total: ${totalProcessedFiles} files, ${allChunks.length} chunks to index\n`);

    // Ensure collection exists
    await ensureCollection();

    // Process chunks in batches to avoid rate limits
    const batchSize = 100;
    let totalIndexed = 0;

    for (let i = 0; i < allChunks.length; i += batchSize) {
        const batch = allChunks.slice(i, i + batchSize);
        console.log(`\n📦 Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(allChunks.length / batchSize)} (${batch.length} chunks)`);

        // Extract text content for embedding generation
        const texts = batch.map(chunk => chunk.content.substring(0, 8192)); // Limit text length for embedding API

        // Generate embeddings
        const embeddings = await generateEmbeddings(texts);

        // Prepare points for Qdrant
        const points = batch.map((chunk, index) => {
            const vector = embeddings[index];
            const id = `${chunk.metadata.source_file}-${chunk.metadata.chunk_index}-${Date.now()}-${Math.random()}`;

            return {
                id: id,
                vector: vector,
                payload: {
                    content: chunk.content,
                    source_file: chunk.metadata.source_file,
                    chunk_index: chunk.metadata.chunk_index,
                    collection: chunk.metadata.collection
                }
            };
        });

        // Upsert to Qdrant
        try {
            await qdrant.upsert(QDRANT_COLLECTION, {
                points: points
            });

            totalIndexed += batch.length;
            console.log(`   ✅ Indexed ${batch.length} chunks (Total: ${totalIndexed}/${allChunks.length})`);
        } catch (error) {
            console.error(`❌ Error upserting batch:`, error.message);
            throw error;
        }
    }

    console.log('\n🎉 Indexing completed successfully!');
    console.log(`📈 Indexed ${totalProcessedFiles} files with ${totalIndexed} chunks into "${QDRANT_COLLECTION}" collection`);

    return {
        status: 'completed',
        message: `Successfully indexed ${totalProcessedFiles} files with ${totalIndexed} chunks`,
        indexed_files: totalProcessedFiles,
        total_chunks: totalIndexed,
        collection_name: QDRANT_COLLECTION
    };
}

/**
 * Main execution function
 */
async function main() {
    console.log('🚀 Book Indexing Script Starting...\n');

    try {
        const result = await indexBooks();
        console.log('\n✅ Script completed successfully!');
        console.log('📋 Result:', result);
        process.exit(0);
    } catch (error) {
        console.error('\n❌ Script failed with error:', error.message);
        console.error('Stack trace:', error.stack);
        process.exit(1);
    }
}

// Run the script if this file is executed directly
if (require.main === module) {
    main();
}

module.exports = { indexBooks, readMarkdownFiles, chunkMarkdownContent };