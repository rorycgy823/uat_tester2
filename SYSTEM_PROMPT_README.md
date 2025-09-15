# System Prompt Functionality

This document describes the system prompt functionality added to the UAT testing application.

## Overview

The system prompt functionality allows users to define a persistent role and behavior for the AI assistant that is prepended to all conversations. This is particularly useful for UAT testing where we want the AI to consistently act as a quality assurance specialist.

## Implementation Details

### Global Variables

Two global variables have been added to `app_chat.py`:

1. `SYSTEM_PROMPT` - Defines the AI's role and behavior
2. `PROMPT_TEMPLATE` - Defines the format for user instructions (unchanged)

### Prompt Construction

The `generate_response` function has been updated to construct prompts in this order:

1. System Prompt (if defined)
2. Conversation History
3. Current User Prompt (using PROMPT_TEMPLATE)

This ensures that the AI always has context about its role before processing the conversation.

### Settings Page

The settings page (`templates/settings.html`) has been enhanced to include:

1. A textarea for configuring the system prompt
2. A separate section for the instruction template
3. Dedicated form action for updating the system prompt

### Routes

A new route has been added to handle system prompt updates:

- `POST /update_system_prompt` - Updates the global SYSTEM_PROMPT variable

## Usage

### Default Behavior

By default, the system prompt is set to:

```
You are a helpful AI assistant specialized in UAT (User Acceptance Testing) and software quality assurance. 
You excel at generating comprehensive test cases from user stories, identifying test variables, and providing detailed testing guidance.

When generating test cases:
1. Consider both happy path and edge cases
2. Include functional, regression, and integration testing scenarios
3. Identify specific UI elements, data inputs, and expected outcomes
4. Structure test cases with clear steps and expected results

When helping with general questions:
1. Provide clear, concise, and accurate information
2. If you're unsure about something, admit it rather than guess
3. Focus on practical solutions and best practices
```

### Customizing the System Prompt

1. Navigate to the Settings page using the gear icon in the main chat interface
2. Modify the system prompt in the provided textarea
3. Click "Save System Prompt" to apply changes
4. The new system prompt will be used in all subsequent conversations

### Customizing the Instruction Template

1. Navigate to the Settings page
2. Modify the instruction template in the provided textarea
3. Click "Save Template" to apply changes
4. The new template will be used for all subsequent user prompts

## Testing

A test script (`test_system_prompt.py`) has been created to verify the functionality:

1. System prompt integration
2. Prompt construction logic
3. Settings page configuration
4. Route availability

To run the tests:

```bash
python test_system_prompt.py
```

## Benefits

1. **Consistent Role**: The AI always understands its role as a UAT specialist
2. **Customizable**: Users can modify the system prompt for different testing scenarios
3. **Separation of Concerns**: System prompt and instruction template are managed separately
4. **Enhanced UAT Testing**: Better test case generation and variable identification
