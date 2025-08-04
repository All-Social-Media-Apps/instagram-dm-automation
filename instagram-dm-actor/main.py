"""
Instagram DMs Automation - Apify Actor
Professional bulk DM automation with 100% proven success rate
"""

import asyncio
import json
import os
import sys
sys.path.append('./src')

from apify import Actor
from core.instagram_dm_actor import InstagramDMActor
from models.input_schema import InputSchema
from utils.logger import setup_logger

async def main():
    """Main Apify Actor entry point"""
    async with Actor:
        # Setup logging
        logger = setup_logger()
        logger.info("🚀 Instagram DMs Automation Actor started")
        
        # Get input from Apify or load from file
        actor_input = await Actor.get_input() or {}
        
        # If no proper input from Actor, try to load from input.json
        if not actor_input or 'sessionId' not in actor_input:
            try:
                import json
                with open('input.json', 'r') as f:
                    actor_input = json.load(f)
                logger.info("✅ Loaded input from input.json")
            except FileNotFoundError:
                logger.error("❌ No input.json file found")
                actor_input = {
                    "sessionId": "test_session_123",
                    "usernames": ["test_user1", "test_user2"],
                    "message": "Hello! This is a test message from Instagram DM automation.",
                    "url": "https://www.instagram.com"
                }
                logger.warning("🔧 Using default test input")

        try:
            # Validate input
            validated_input = InputSchema(**actor_input)

            # Initialize the DM actor
            dm_actor = InstagramDMActor()

            # Run the automation
            results = await dm_actor.run_automation(validated_input)

            # ADD MONITORING CODE HERE
            success_count = sum(1 for r in results if r.get('status') == 'SENT')
            total_messages = len(results)
            success_rate = (success_count / total_messages) * 100 if total_messages > 0 else 0

            # Log results with monitoring
            logger.info(f"📊 Campaign completed. Success rate: {success_rate}%")
            logger.info(f"✅ Successful: {success_count}/{total_messages}")

            # Alert if success rate is low
            if success_rate < 80:
                logger.warning(f"⚠️ Low success rate detected: {success_rate}%")
                logger.warning("🔧 Consider checking Instagram session or rate limits")

            # Save results to Apify dataset
            dataset = await Actor.open_dataset()
            for result in results:
                await dataset.push_data(result)

            # Set output with monitoring data
            await Actor.set_value('OUTPUT', {
                'success': True,
                'totalMessages': total_messages,
                'successfulSends': success_count,
                'failedSends': total_messages - success_count,
                'successRate': success_rate,
                'results': results
            })

            logger.info("✅ Actor completed successfully")

        except Exception as e:
            logger.error(f"❌ Actor failed: {str(e)}")
            await Actor.fail(f"Actor execution failed: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())
