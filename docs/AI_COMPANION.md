# AI Reflection Companion

The AI Reflection Companion is a thoughtful, personalized feature in Smriti that helps users deepen their reflection practice through AI-generated prompts, contemplative questions, and meditation guidance.

## Features

### 1. Reflection Prompts
Receive personalized prompts to guide your inner exploration.

**How to use:**
1. Open the Companion from the sparkles icon in the header or the "Reflection Companion" card on the home screen
2. Go to the "Reflect" tab
3. Optionally select your current mood (Calm, Unsettled, Grateful, Reflective, or Seeking)
4. Tap "Receive Guidance"

**Personalization:**
- If you've opted in to reflection analysis and have past posts, prompts will be tailored based on themes from your reflections
- Without opt-in, you still receive thoughtful, generic prompts

### 2. Contemplative Questions
Discover meaningful questions to illuminate your path.

**How to use:**
1. Go to the "Contemplate" tab
2. Choose a theme:
   - **Self** - Know thyself
   - **Relationships** - Connection with others
   - **Purpose** - Life direction
   - **Presence** - Being here now
   - **Gratitude** - Appreciation
3. Select depth level:
   - **Gentle** - Light reflection
   - **Moderate** - Deeper inquiry
   - **Deep** - Profound exploration
4. Tap "Receive Guidance"

Each question comes with follow-up prompts for deeper exploration.

### 3. Meditation Guidance
Let gentle guidance lead you into peaceful presence.

**How to use:**
1. Go to the "Meditate" tab
2. Choose your practice type:
   - **Sankalpam** - Set a sacred intention (can enter custom intention)
   - **Breath Awareness** - Simple presence with the breath
   - **Deep Contemplation** - Journey into inner stillness
3. Select duration: 5, 10, 15, or 20 minutes
4. Tap "Receive Guidance"
5. View the full meditation with Opening, Settling, Guidance intervals, and Closing sections

### 4. Conversation History
Review your past interactions with the Companion.

**How to use:**
1. Go to the "History" tab
2. Tap any entry to view the full content
3. Long-press or tap the delete button to remove an entry
4. Use "Clear All" to delete all history

## Privacy Considerations

### Data Collection
- **Conversation History**: All interactions are saved to your history for your reference
- **Past Reflections**: Only used for personalization if you explicitly opt-in
- **No Third-Party Sharing**: Your reflection data is never shared with third parties

### Opt-In Reflection Analysis
The Companion can use your past posts to personalize prompts. This feature requires explicit opt-in:

1. Your posts are analyzed locally to extract themes
2. Themes (not full content) are used to personalize prompts
3. You can opt-out at any time in settings

**To enable:**
- In the Companion, check the "Use my reflections for personalization" option

### Data Retention
- Conversation history is retained until you delete it
- You can delete individual entries or clear all history
- Deleting history does not affect your posts

### AI Processing
- AI-generated content is created using secure, privacy-focused providers
- Your data is processed transiently and not retained by AI providers
- No training on user data

## API Endpoints

### Settings
- `GET /api/v1/ai/companion/settings` - Get user settings
- `PUT /api/v1/ai/companion/settings` - Update settings

### Generation
- `POST /api/v1/ai/companion/prompt` - Generate reflection prompt
- `POST /api/v1/ai/companion/question` - Generate contemplative question
- `POST /api/v1/ai/companion/meditation` - Generate meditation guidance
- `POST /api/v1/ai/companion/tts` - Text-to-speech (if supported)

### History
- `GET /api/v1/ai/companion/history` - Get conversation history (paginated)
- `DELETE /api/v1/ai/companion/history/{entry_id}` - Delete single entry
- `DELETE /api/v1/ai/companion/history` - Delete all history

### Analysis
- `POST /api/v1/ai/companion/analyze` - Analyze reflection patterns (requires opt-in)

## Rate Limits

To ensure service quality, the Companion has the following rate limits:

| Action | Limit |
|--------|-------|
| Reflection Prompts | 30 per hour |
| Contemplative Questions | 30 per hour |
| Meditation Guidance | 20 per hour |
| Reflection Analysis | 5 per hour |

## Error Handling

### When AI is Unavailable
If the AI service is temporarily unavailable:
- The app displays a calm message: "A moment of stillness... Something interrupted our connection."
- You can retry by tapping "Try Again"
- Fallback content may be provided for basic prompts

### Network Issues
- The app handles offline scenarios gracefully
- Loading states show a breathing orb animation with rotating spiritual messages

## Design Philosophy

The Companion is designed to feel:
- **Spiritual, not technical** - Language and UI evoke calm contemplation
- **Supportive, not prescriptive** - Guidance without judgment
- **Personal, not generic** - Tailored to your journey (with opt-in)
- **Minimal, not cluttered** - Clean interface that promotes focus

## Technical Notes

### Frontend
- Built with React Native
- Uses custom hooks (`useCompanion`) for state management
- Animated breathing orb for loading states
- Modal presentations for meditation guidance

### Backend
- FastAPI with async endpoints
- MongoDB for history storage
- Pluggable AI provider system (OpenAI, Anthropic, or mock for testing)
- In-memory rate limiting per user

### Testing
- 102+ unit and integration tests for companion module
- Tests cover all API endpoints, personalization logic, and edge cases
- Mock AI provider for reliable testing

## Troubleshooting

**Prompts seem generic:**
- Check if you've opted in to reflection analysis
- Ensure you have at least a few posts for theme extraction

**History not loading:**
- Pull down to refresh
- Check your network connection

**Rate limit reached:**
- Wait for the limit to reset (limits are per-hour)
- Consider spacing out your requests

**Meditation guidance too short:**
- Select a longer duration (15-20 minutes)
- Enable interval guidance for more content
