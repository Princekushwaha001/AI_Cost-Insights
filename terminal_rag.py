# #!/usr/bin/env python3

# working fine need prompt improvement
# """
# Terminal-based RAG System Interface
# Run this script to interact with your FinOps RAG system via command line.
# """
#
# import os
# import sys
# import logging
# from pathlib import Path
#
# # Add your app directory to Python path if needed
# # sys.path.insert(0, str(Path(__file__).parent))
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts import build_prompt, get_system_prompt
#
# # Configure logging
# logging.basicConfig(level=logging.WARNING)  # Reduce noise in terminal
# logger = logging.getLogger(__name__)
#
#
# def format_context(results):
#     """Format query results into context string for prompts"""
#     if not results:
#         return "No relevant context found in the database."
#
#     context_parts = []
#     for i, result in enumerate(results, 1):
#         context_parts.append(
#             f"Source {i}: {result['table_name']} table, row {result['row_id']} "
#             f"(score: {result['score']:.3f})\n{result['snippet']}"
#         )
#
#     return "\n\n".join(context_parts)
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question through the RAG system"""
#     print(f"\n🔍 Searching for relevant context...")
#
#     # Get relevant context from your embedder
#     results = query_knn(question, k=k)
#
#     if not results:
#         print("❌ No relevant context found. Make sure your data is embedded.")
#         return None
#
#     # Format context for prompt
#     context = format_context(results)
#
#     # Build prompt using your existing system
#     prompt = build_prompt(context, question)
#
#     print(f"✅ Found {len(results)} relevant sources")
#     return {
#         'prompt': prompt,
#         'context': context,
#         'sources': results,
#         'question': question
#     }
#
#
# def display_response(response_data):
#     """Display the formatted response"""
#     if not response_data:
#         return
#
#     print("\n" + "=" * 80)
#     print("📋 FINBOT RESPONSE")
#     print("=" * 80)
#
#     # In a real implementation, you'd send the prompt to your LLM
#     # For now, we'll show the formatted prompt and context
#     print("\n🤖 Generated Prompt:")
#     print("-" * 40)
#     print(response_data['prompt'])
#
#     print(f"\n📊 Sources Used ({len(response_data['sources'])}):")
#     print("-" * 40)
#     for i, source in enumerate(response_data['sources'], 1):
#         print(f"{i}. Table: {source['table_name']}, Row: {source['row_id']}, Score: {source['score']:.3f}")
#
#
# def show_help():
#     """Display help information"""
#     help_text = """
# 🚀 FinOps RAG Terminal Interface
# ================================
#
# Commands:
#   - Type your question and press Enter
#   - 'help' or '?' - Show this help
#   - 'embed' - Re-embed all data
#   - 'status' - Show system status
#   - 'quit', 'exit', or Ctrl+C - Exit
#
# Examples:
#   "Which compute resources have the highest cost?"
#   "Show me storage costs for Q3 2025"
#   "Give cost-saving suggestions for storage-heavy workloads"
#
# The system will search your billing and resources data and provide
# contextual responses based on your stored CSV data.
#     """
#     print(help_text)
#
#
# def check_system_status():
#     """Check if the system is ready"""
#     try:
#         # Test if FAISS index exists
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         if not index_path.exists():
#             print("⚠️  FAISS index not found. Run 'embed' command to create it.")
#             return False
#
#         print("✅ System ready - FAISS index found")
#         return True
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Main terminal interface loop"""
#     print("🚀 Starting FinOps RAG Terminal Interface...")
#
#     # Check system status
#     system_ready = check_system_status()
#
#     show_help()
#
#     print("\nType 'help' for commands or start asking questions!")
#     print("Type 'quit' to exit.\n")
#
#     # Main interaction loop
#     while True:
#         try:
#             # Get user input
#             user_input = input("💬 FinBot> ").strip()
#
#             # Handle empty input
#             if not user_input:
#                 continue
#
#             # Handle commands
#             if user_input.lower() in ['quit', 'exit', 'q']:
#                 print("👋 Goodbye!")
#                 break
#
#             elif user_input.lower() in ['help', '?']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Embedding all data... This may take a moment.")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"✅ Embedding complete!")
#                     print(f"   - Added vectors: {stats['added_vectors']}")
#                     print(f"   - Skipped existing: {stats['skipped_existing']}")
#                     print(f"   - Updated metadata: {stats['updated_metadata']}")
#                     system_ready = True
#                 except Exception as e:
#                     print(f"❌ Embedding failed: {e}")
#                 continue
#
#             elif user_input.lower() == 'status':
#                 check_system_status()
#                 continue
#
#             # Handle regular questions
#             if not system_ready:
#                 print("⚠️  System not ready. Please run 'embed' command first.")
#                 continue
#
#             # Process the question
#             response_data = process_query(user_input)
#             display_response(response_data)
#
#             # Note about LLM integration
#             print("\n💡 Note: This shows the RAG context and prompt. To get actual")
#             print("   LLM responses, integrate with OpenAI, Ollama, or another LLM.")
#
#         except KeyboardInterrupt:
#             print("\n👋 Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Error: {e}")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


def format_context_for_humans(results):
    """Format query results in a business-friendly way"""
    if not results:
        return "No relevant information found in your billing and resource data."

    context_parts = []
    seen_content = set()  # Avoid duplicates

    for i, result in enumerate(results, 1):
        # Skip duplicate content
        if result['snippet'] in seen_content:
            continue
        seen_content.add(result['snippet'])

        # Format based on table type
        if result['table_name'] == 'billing':
            context_parts.append(f"💰 From your billing records: {result['snippet']}")
        elif result['table_name'] == 'resources':
            context_parts.append(f"🔧 From your resource inventory: {result['snippet']}")
        else:
            context_parts.append(f"📋 From your records: {result['snippet']}")

    return "\n".join(context_parts)


def display_friendly_response(response_data):
    """Display response in a more user-friendly format"""
    if not response_data:
        return

    print("\n" + "=" * 60)
    print("💼 FinBot Response")
    print("=" * 60)

    # Show the context in a readable way
    print("\n📊 What I found in your data:")
    print("-" * 30)
    unique_sources = []
    seen = set()
    for source in response_data['sources']:
        if source['snippet'] not in seen and source['snippet']:
            seen.add(source['snippet'])
            if source['table_name'] == 'billing':
                unique_sources.append(f"💰 Billing: {source['snippet']}")
            elif source['table_name'] == 'resources':
                unique_sources.append(f"🔧 Resource: {source['snippet']}")

    for source in unique_sources[:5]:  # Show max 5 unique sources
        print(f"   {source}")

    print(f"\n🤖 FinBot Analysis:")
    print("-" * 30)

    # In a real implementation, this would be the LLM response
    # For now, show a sample business-friendly response
    print("Based on your data, I can help you understand your cloud spending.")
    print("To get the actual analysis, connect this system to an AI service like OpenAI.")

    print(f"\n📈 Data Sources: Found {len([s for s in response_data['sources'] if s['snippet']])} relevant records")


# # Update the process_query function
# def process_query(question: str, k: int = 5):
#     """Process a user question through the RAG system"""
#     print(f"\n🔍 Looking through your financial records...")
#
#     # Get relevant context
#     results = query_knn(question, k=k)
#
#     if not results:
#         print("❌ I couldn't find relevant information in your data.")
#         print("💡 Make sure you've run the 'embed' command to process your CSV files.")
#         return None
#
#     # Remove duplicates and None values
#     unique_results = []
#     seen_snippets = set()
#     for result in results:
#         if result['snippet'] and result['snippet'] not in seen_snippets:
#             unique_results.append(result)
#             seen_snippets.add(result['snippet'])
#
#     if not unique_results:
#         print("❌ Found some records but they don't contain useful information.")
#         return None
#
#     # Format context for humans
#     context = format_context_for_humans(unique_results)
#
#     # Build human-friendly prompt
#     from backend.prompts import build_simple_prompt  # Use the simpler version
#     prompt = build_simple_prompt(context, question)
#
#     print(f"✅ Found {len(unique_results)} relevant pieces of information")
#     return {
#         'prompt': prompt,
#         'context': context,
#         'sources': unique_results,
#         'question': question
#     }


# # !/usr/bin/env python3
# """
# Terminal-based RAG System Interface - Human Friendly Version
# Run this script to interact with your FinOps RAG system via command line.
# """
#
# import os
# import sys
# import logging
# from pathlib import Path
#
# # Add your app directory to Python path if needed
# # sys.path.insert(0, str(Path(__file__).parent))
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts import build_simple_prompt, get_human_friendly_examples
#
# # Configure logging to reduce noise in terminal
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
#
# def format_context_for_humans(results):
#     """Format query results in a business-friendly way"""
#     if not results:
#         return "No relevant information found in your billing and resource data."
#
#     context_parts = []
#     seen_content = set()  # Avoid duplicates
#
#     for result in results:
#         # Skip duplicate content or empty snippets
#         if not result.get('snippet') or result['snippet'] in seen_content:
#             continue
#         seen_content.add(result['snippet'])
#
#         # Format based on table type with business context
#         snippet = result['snippet']
#         table_name = result.get('table_name', 'unknown')
#
#         if table_name == 'billing':
#             # Parse billing info to make it more readable
#             if 'Invoice' in snippet and 'cost' in snippet:
#                 try:
#                     parts = snippet.split()
#                     month_info = ""
#                     cost_info = ""
#                     service_info = ""
#
#                     for i, part in enumerate(parts):
#                         if part.startswith('2025-'):
#                             month_info = f"In {part}"
#                         elif part == 'cost' and i + 1 < len(parts):
#                             try:
#                                 cost_val = float(parts[i + 1])
#                                 cost_info = f"${cost_val:,.2f}"
#                             except:
#                                 cost_info = parts[i + 1]
#                         elif part == 'service' and i + 1 < len(parts):
#                             service_info = f"for {parts[i + 1]} services"
#
#                     formatted = f"💰 {month_info}, you spent {cost_info} {service_info}"
#                     if formatted.count('None') == 0:  # Only use if parsing worked
#                         context_parts.append(formatted)
#                         continue
#                 except:
#                     pass
#
#             # Fallback to generic billing format
#             context_parts.append(f"💰 From your billing records: {snippet}")
#
#         elif table_name == 'resources':
#             context_parts.append(f"🔧 From your resource inventory: {snippet}")
#         else:
#             context_parts.append(f"📋 From your data: {snippet}")
#
#     return "\n".join(context_parts[:5])  # Limit to top 5 most relevant
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question through the RAG system"""
#     print(f"\n🔍 Looking through your financial records...")
#
#     # Clean up the question if it's in JSON format (common user error)
#     clean_question = question
#     if question.strip().startswith('{') and '"query"' in question:
#         try:
#             import json
#             data = json.loads(question)
#             clean_question = data.get('query', question)
#         except:
#             # If JSON parsing fails, try simple string extraction
#             if '"query":' in question:
#                 try:
#                     start = question.find('"query":') + 8
#                     end = question.find('"', start + 1)
#                     if start > 7 and end > start:
#                         clean_question = question[start:end].strip(' "')
#                 except:
#                     pass
#
#     # Get relevant context
#     results = query_knn(clean_question, k=k)
#
#     if not results:
#         print("❌ I couldn't find relevant information in your data.")
#         print("💡 Make sure you've run the 'embed' command to process your CSV files.")
#         return None
#
#     # Remove duplicates and None values
#     unique_results = []
#     seen_snippets = set()
#     for result in results:
#         snippet = result.get('snippet')
#         if snippet and snippet.strip() and snippet not in seen_snippets:
#             # Skip entries that are just "None" or empty
#             if snippet.strip() != 'None' and len(snippet.strip()) > 5:
#                 unique_results.append(result)
#                 seen_snippets.add(snippet)
#
#     if not unique_results:
#         print("❌ Found some records but they don't contain useful information.")
#         print("💡 Your data might need better formatting or more detailed information.")
#         return None
#
#     # Format context for humans
#     context = format_context_for_humans(unique_results)
#
#     # Build human-friendly prompt
#     prompt = build_simple_prompt(context, clean_question)
#
#     print(f"✅ Found {len(unique_results)} relevant pieces of information")
#     return {
#         'prompt': prompt,
#         'context': context,
#         'sources': unique_results,
#         'question': clean_question,
#         'original_question': question
#     }
#
#
# def display_friendly_response(response_data):
#     """Display response in a user-friendly format"""
#     if not response_data:
#         return
#
#     print("\n" + "=" * 70)
#     print("💼 FinBot - Your Cloud Cost Assistant")
#     print("=" * 70)
#
#     # Show what we found in plain English
#     print(f"\n🎯 Your Question: {response_data['question']}")
#
#     print("\n📊 What I Found in Your Data:")
#     print("-" * 40)
#
#     # Group and display sources by type
#     billing_sources = []
#     resource_sources = []
#
#     for source in response_data['sources']:
#         if source.get('table_name') == 'billing' and source.get('snippet'):
#             billing_sources.append(source['snippet'])
#         elif source.get('table_name') == 'resources' and source.get('snippet'):
#             resource_sources.append(source['snippet'])
#
#     if billing_sources:
#         print("💰 Billing Information:")
#         for i, billing in enumerate(billing_sources[:3], 1):
#             # Try to make billing info more readable
#             readable_billing = billing
#             try:
#                 if 'Invoice' in billing and 'cost' in billing:
#                     parts = billing.split()
#                     for j, part in enumerate(parts):
#                         if part.startswith('2025-'):
#                             readable_billing = readable_billing.replace(part, f"({part})")
#                         elif 'cost' in parts and j + 1 < len(parts) and parts[j] == 'cost':
#                             try:
#                                 cost_val = float(parts[j + 1])
#                                 readable_billing = readable_billing.replace(
#                                     f"cost {parts[j + 1]}",
#                                     f"cost ${cost_val:,.2f}"
#                                 )
#                             except:
#                                 pass
#             except:
#                 pass
#             print(f"   {i}. {readable_billing}")
#
#     if resource_sources:
#         print("\n🔧 Resource Information:")
#         for i, resource in enumerate(resource_sources[:3], 1):
#             print(f"   {i}. {resource}")
#
#     print(f"\n🤖 AI Analysis:")
#     print("-" * 40)
#     print("I've prepared a detailed analysis based on your data.")
#     print("To see the full AI response, you'll need to connect an AI service like:")
#     print("• OpenAI GPT")
#     print("• Google Gemini")
#     print("• Local models like Ollama")
#
#     print("\n📋 Technical Prompt (for AI integration):")
#     print("-" * 50)
#     print(response_data['prompt'][:500] + "..." if len(response_data['prompt']) > 500 else response_data['prompt'])
#
#     print(f"\n📈 Summary: Analyzed {len(response_data['sources'])} relevant records from your financial data")
#
#
# def show_help():
#     """Display help information"""
#     help_text = """
# 🚀 FinBot - Cloud Cost Management Assistant
# ==========================================
#
# This tool helps you understand your cloud spending in plain English!
#
# 💬 COMMANDS:
# • Just type your question and press Enter
# • 'help' or '?' - Show this help menu
# • 'embed' - Process your CSV data (do this first!)
# • 'status' - Check if system is ready
# • 'examples' - Show example questions
# • 'quit' or 'exit' - Leave the program
#
# 🎯 EXAMPLE QUESTIONS:
# • "What did we spend on storage in July 2025?"
# • "Which service costs us the most money?"
# • "Show me all costs for July 2025"
# • "What are our biggest expenses?"
# • "How much did we spend on compute resources?"
#
# 💡 TIPS:
# • Ask questions in plain English - no need for technical terms
# • The system searches through your billing and resource data
# • Make sure to run 'embed' command first to process your data
# • Questions about specific months work best (like "July 2025")
#
# 🔧 FIRST TIME SETUP:
# 1. Run: embed
# 2. Wait for processing to complete
# 3. Start asking questions!
# """
#     print(help_text)
#
#
# def show_examples():
#     """Show example questions and responses"""
#     print("\n🎯 Example Questions You Can Ask:")
#     print("=" * 50)
#
#     examples = get_human_friendly_examples()
#     for i, example in enumerate(examples, 1):
#         print(f"\n{i}. Question: {example['q']}")
#         print(f"   Expected Response: {example['a'][:100]}...")
#
#     print(f"\n💡 Try asking similar questions about your own data!")
#
#
# def check_system_status():
#     """Check if the system is ready"""
#     try:
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         print("\n🔍 System Status Check:")
#         print("-" * 30)
#
#         if not index_path.exists():
#             print("❌ Data not processed yet")
#             print("   Run 'embed' command to process your CSV files")
#             return False
#
#         file_size = index_path.stat().st_size
#         print(f"✅ Data processed successfully")
#         print(f"   Index file size: {file_size:,} bytes")
#         print("   System ready for questions!")
#         return True
#
#     except ImportError:
#         print("❌ Configuration file not found")
#         print("   Check your app.configs module")
#         return False
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Main terminal interface loop"""
#     print("🚀 Starting FinBot - Your Friendly Cloud Cost Assistant")
#     print("=" * 60)
#
#     # Check system status
#     system_ready = check_system_status()
#
#     if not system_ready:
#         print("\n⚠️  System not ready! Please run 'embed' command first.")
#
#     show_help()
#
#     print("\n🗣️  Ready to help! Type your question or 'help' for assistance.")
#     print("💡 Remember: Ask in plain English, like 'What did we spend in July?'")
#
#     # Main interaction loop
#     while True:
#         try:
#             # Get user input with friendly prompt
#             user_input = input("\n💬 Ask FinBot> ").strip()
#
#             # Handle empty input
#             if not user_input:
#                 print("🤔 Please ask me a question about your cloud costs!")
#                 continue
#
#             # Handle commands
#             if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
#                 print("👋 Thanks for using FinBot! Have a great day!")
#                 break
#
#             elif user_input.lower() in ['help', '?', 'h']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() in ['examples', 'example', 'ex']:
#                 show_examples()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Processing your data... This might take a few minutes.")
#                 print("   ⏳ Analyzing CSV files and creating search index...")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"\n🎉 Success! Your data is now ready for questions!")
#                     print(f"   📊 Processed records:")
#                     print(f"   • Added: {stats['added_vectors']} new entries")
#                     print(f"   • Skipped: {stats['skipped_existing']} existing entries")
#                     print(f"   • Updated: {stats['updated_metadata']} metadata records")
#                     system_ready = True
#                     print("\n💡 Now you can start asking questions about your costs!")
#                 except Exception as e:
#                     print(f"❌ Processing failed: {e}")
#                     print("   Please check your CSV files and database connection.")
#                 continue
#
#             elif user_input.lower() in ['status', 'check']:
#                 check_system_status()
#                 continue
#
#             # Handle regular questions
#             if not system_ready:
#                 print("⚠️  I need to process your data first.")
#                 print("   Please run 'embed' command to get started.")
#                 continue
#
#             # Process the question
#             print("🔍 Let me search through your financial data...")
#             response_data = process_query(user_input)
#
#             if response_data:
#                 display_friendly_response(response_data)
#             else:
#                 print("😕 I couldn't find relevant information for your question.")
#                 print("💡 Try rephrasing your question or check if your data covers that time period.")
#                 print("   Example: 'What did we spend on storage in July 2025?'")
#
#         except KeyboardInterrupt:
#             print("\n\n👋 Thanks for using FinBot! Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Something went wrong: {e}")
#             print("💡 Please try rephrasing your question or check 'help' for examples.")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


# # !/usr/bin/env python3
# """
# Terminal-based RAG System Interface - Human Friendly Version with Response Generation
# Run this script to interact with your FinOps RAG system via command line.
# """
#
# import os
# import sys
# import logging
# import re
# from pathlib import Path
# from collections import defaultdict
#
# # Add your app directory to Python path if needed
# # sys.path.insert(0, str(Path(__file__).parent))
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts import build_simple_prompt, get_human_friendly_examples
#
# # Configure logging to reduce noise in terminal
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
#
# def parse_billing_data(sources):
#     """Parse billing sources into structured data"""
#     billing_data = []
#     resource_data = []
#
#     for source in sources:
#         snippet = source.get('snippet', '')
#         table_name = source.get('table_name', '')
#
#         if table_name == 'billing' and snippet:
#             # Parse billing information
#             billing_info = {}
#
#             # Extract month
#             month_match = re.search(r'2025-(\d{2})', snippet)
#             if month_match:
#                 month_num = month_match.group(1)
#                 month_names = {
#                     '01': 'January', '02': 'February', '03': 'March',
#                     '04': 'April', '05': 'May', '06': 'June',
#                     '07': 'July', '08': 'August', '09': 'September',
#                     '10': 'October', '11': 'November', '12': 'December'
#                 }
#                 billing_info['month'] = month_names.get(month_num, f"Month {month_num}")
#                 billing_info['month_code'] = f"2025-{month_num}"
#
#             # Extract service
#             service_match = re.search(r'service (\w+)', snippet)
#             if service_match:
#                 billing_info['service'] = service_match.group(1)
#
#             # Extract cost
#             cost_match = re.search(r'cost (\d+\.?\d*)', snippet)
#             if cost_match:
#                 try:
#                     billing_info['cost'] = float(cost_match.group(1))
#                 except:
#                     billing_info['cost'] = 0
#
#             # Extract account
#             account_match = re.search(r'account ([\w-]+)', snippet)
#             if account_match:
#                 billing_info['account'] = account_match.group(1)
#
#             if billing_info:
#                 billing_data.append(billing_info)
#
#         elif table_name == 'resources' and snippet:
#             resource_data.append({'snippet': snippet})
#
#     return billing_data, resource_data
#
#
# def generate_human_response(question, billing_data, resource_data):
#     """Generate a human-readable response based on the data"""
#     if not billing_data and not resource_data:
#         return "I couldn't find any relevant financial information in your records for this question. Please make sure your data has been processed with the 'embed' command and try rephrasing your question."
#
#     response_parts = []
#
#     # Analyze the question to understand what they're asking for
#     question_lower = question.lower()
#
#     # Check if asking about specific month
#     month_match = re.search(r'2025-(\d{2})', question)
#     asking_about_month = month_match.group(0) if month_match else None
#
#     if asking_about_month:
#         month_num = asking_about_month.split('-')[1]
#         month_names = {
#             '01': 'January', '02': 'February', '03': 'March',
#             '04': 'April', '05': 'May', '06': 'June',
#             '07': 'July', '08': 'August', '09': 'September',
#             '10': 'October', '11': 'November', '12': 'December'
#         }
#         readable_month = month_names.get(month_num, f"month {month_num}")
#
#         # Filter billing data for that month
#         month_data = [b for b in billing_data if b.get('month_code') == asking_about_month]
#
#         if month_data:
#             total_cost = sum(b.get('cost', 0) for b in month_data)
#             services = {}
#
#             for item in month_data:
#                 service = item.get('service', 'Unknown')
#                 cost = item.get('cost', 0)
#                 if service in services:
#                     services[service] += cost
#                 else:
#                     services[service] = cost
#
#             # Generate response
#             response_parts.append(
#                 f"Based on your {readable_month} 2025 billing records, I found {len(month_data)} transactions totaling ${total_cost:,.2f}.")
#
#             if len(services) == 1:
#                 service_name = list(services.keys())[0]
#                 service_cost = list(services.values())[0]
#                 response_parts.append(
#                     f"You used {service_name} services exclusively that month, spending ${service_cost:,.2f}.")
#
#                 # Add context about the service
#                 if service_name.lower() == 'compute':
#                     response_parts.append(
#                         "Compute services include your servers, virtual machines, and processing power that run your applications.")
#                 elif service_name.lower() == 'storage':
#                     response_parts.append(
#                         "Storage services cover the cost of keeping your files, databases, and backups safe in the cloud.")
#                 elif service_name.lower() == 'ai':
#                     response_parts.append(
#                         "AI services include machine learning, language processing, and other artificial intelligence capabilities.")
#                 elif service_name.lower() == 'db':
#                     response_parts.append(
#                         "Database services handle storing and managing your structured business data.")
#                 else:
#                     response_parts.append(f"{service_name} services are part of your cloud infrastructure costs.")
#
#             else:
#                 # Multiple services
#                 sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#                 response_parts.append(f"You used {len(services)} different services:")
#
#                 for i, (service, cost) in enumerate(sorted_services):
#                     percentage = (cost / total_cost) * 100
#                     response_parts.append(f"• {service}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#                 # Highlight the biggest expense
#                 biggest_service, biggest_cost = sorted_services[0]
#                 response_parts.append(
#                     f"Your largest expense was {biggest_service} services, representing {(biggest_cost / total_cost) * 100:.1f}% of your {readable_month} cloud spending.")
#         else:
#             response_parts.append(f"I couldn't find any billing records for {readable_month} 2025.")
#             response_parts.append(
#                 "This might mean you didn't have any charges that month, or the data might not be available in your records.")
#
#     # General service and cost questions
#     elif any(word in question_lower for word in ['service', 'cost', 'spend', 'expense']):
#         if billing_data:
#             total_cost = sum(b.get('cost', 0) for b in billing_data)
#             services = {}
#             months = set()
#
#             for item in billing_data:
#                 service = item.get('service', 'Unknown')
#                 cost = item.get('cost', 0)
#                 month = item.get('month_code', '')
#
#                 if service in services:
#                     services[service] += cost
#                 else:
#                     services[service] = cost
#
#                 if month:
#                     months.add(month)
#
#             # Generate summary
#             time_period = f"across {len(months)} months" if len(
#                 months) > 1 else f"in {list(months)[0] if months else 'the period'}"
#             response_parts.append(
#                 f"Looking at your cloud spending {time_period}, I found a total of ${total_cost:,.2f} in charges.")
#
#             if services:
#                 sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#                 response_parts.append(f"Your services breakdown:")
#
#                 for service, cost in sorted_services[:3]:  # Top 3 services
#                     percentage = (cost / total_cost) * 100
#                     response_parts.append(f"• {service}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#     # If no specific response generated, provide general summary
#     if not response_parts and billing_data:
#         total_records = len(billing_data)
#         total_cost = sum(b.get('cost', 0) for b in billing_data)
#         unique_services = len(set(b.get('service', 'Unknown') for b in billing_data))
#
#         response_parts.append(
#             f"I found {total_records} billing records in your data with a total value of ${total_cost:,.2f}.")
#         response_parts.append(
#             f"This covers {unique_services} different types of cloud services across multiple accounts and time periods.")
#
#     if not response_parts:
#         return "I found some information in your records, but I need more context to provide a specific answer. Try asking about a particular month (like 'July 2025') or specific services (like 'storage costs')."
#
#     return " ".join(response_parts)
#
#
# def format_context_for_humans(results):
#     """Format query results in a business-friendly way"""
#     if not results:
#         return "No relevant information found in your billing and resource data."
#
#     context_parts = []
#     seen_content = set()  # Avoid duplicates
#
#     for result in results:
#         # Skip duplicate content or empty snippets
#         if not result.get('snippet') or result['snippet'] in seen_content:
#             continue
#         seen_content.add(result['snippet'])
#
#         # Format based on table type with business context
#         snippet = result['snippet']
#         table_name = result.get('table_name', 'unknown')
#
#         if table_name == 'billing':
#             context_parts.append(f"💰 From your billing records: {snippet}")
#         elif table_name == 'resources':
#             context_parts.append(f"🔧 From your resource inventory: {snippet}")
#         else:
#             context_parts.append(f"📋 From your data: {snippet}")
#
#     return "\n".join(context_parts[:5])  # Limit to top 5 most relevant
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question through the RAG system"""
#     print(f"\n🔍 Searching through your financial records...")
#
#     # Clean up the question if it's in JSON format
#     clean_question = question
#     if question.strip().startswith('{') and '"query"' in question:
#         try:
#             import json
#             data = json.loads(question)
#             clean_question = data.get('query', question)
#         except:
#             if '"query":' in question:
#                 try:
#                     start = question.find('"query":') + 8
#                     end = question.find('"', start + 1)
#                     if start > 7 and end > start:
#                         clean_question = question[start:end].strip(' "')
#                 except:
#                     pass
#
#     # Get relevant context
#     results = query_knn(clean_question, k=k)
#
#     if not results:
#         print("❌ No relevant information found in your data.")
#         print("💡 Make sure you've run the 'embed' command to process your CSV files.")
#         return None
#
#     # Remove duplicates and None values
#     unique_results = []
#     seen_snippets = set()
#     for result in results:
#         snippet = result.get('snippet')
#         if snippet and snippet.strip() and snippet not in seen_snippets:
#             if snippet.strip() != 'None' and len(snippet.strip()) > 5:
#                 unique_results.append(result)
#                 seen_snippets.add(snippet)
#
#     if not unique_results:
#         print("❌ Found some records but they don't contain useful information.")
#         return None
#
#     # Parse the data for human response generation
#     billing_data, resource_data = parse_billing_data(unique_results)
#
#     # Generate human-readable response
#     human_response = generate_human_response(clean_question, billing_data, resource_data)
#
#     print(f"✅ Found {len(unique_results)} relevant records")
#     return {
#         'question': clean_question,
#         'human_response': human_response,
#         'billing_data': billing_data,
#         'resource_data': resource_data,
#         'sources': unique_results
#     }
#
#
# def display_friendly_response(response_data):
#     """Display the actual human-friendly response"""
#     if not response_data:
#         return
#
#     print("\n" + "=" * 70)
#     print("💼 FinBot - Your Cloud Cost Assistant")
#     print("=" * 70)
#
#     print(f"\n🎯 Your Question: {response_data['question']}")
#
#     print(f"\n🤖 FinBot Analysis:")
#     print("-" * 40)
#     print(response_data['human_response'])
#
#     # Show supporting data if available
#     if response_data['billing_data']:
#         print(f"\n📊 Supporting Data:")
#         print("-" * 25)
#         for i, billing in enumerate(response_data['billing_data'][:3], 1):
#             month = billing.get('month', 'Unknown month')
#             service = billing.get('service', 'Unknown service')
#             cost = billing.get('cost', 0)
#             print(f"   {i}. {month}: {service} - ${cost:,.2f}")
#
#     print(f"\n📈 Data Summary: Analyzed {len(response_data['sources'])} records from your financial database")
#
#
# def show_help():
#     """Display help information"""
#     help_text = """
# 🚀 FinBot - Cloud Cost Management Assistant
# ==========================================
#
# This tool helps you understand your cloud spending in plain English!
#
# 💬 COMMANDS:
# • Just type your question and press Enter
# • 'help' or '?' - Show this help menu
# • 'embed' - Process your CSV data (do this first!)
# • 'status' - Check if system is ready
# • 'examples' - Show example questions
# • 'quit' or 'exit' - Leave the program
#
# 🎯 EXAMPLE QUESTIONS:
# • "What did we spend on storage in July 2025?"
# • "For invoice month 2025-07 what is the service we are using and its cost?"
# • "Which service costs us the most money?"
# • "Show me all costs for July 2025"
# • "What are our biggest expenses?"
# • "How much did we spend on compute resources?"
#
# 💡 TIPS:
# • Ask questions in plain English - no need for technical terms
# • The system searches through your billing and resource data
# • Make sure to run 'embed' command first to process your data
# • Questions about specific months work best (like "July 2025")
#
# 🔧 FIRST TIME SETUP:
# 1. Run: embed
# 2. Wait for processing to complete
# 3. Start asking questions!
# """
#     print(help_text)
#
#
# def show_examples():
#     """Show example questions and responses"""
#     print("\n🎯 Example Questions You Can Ask:")
#     print("=" * 50)
#
#     examples = [
#         "What services did we use in July 2025?",
#         "How much did we spend on storage?",
#         "Which service costs the most?",
#         "Show me our expenses for 2025-07",
#         "What are our main cloud costs?"
#     ]
#
#     for i, example in enumerate(examples, 1):
#         print(f"{i}. {example}")
#
#     print(f"\n💡 Try asking similar questions about your own data!")
#
#
# def check_system_status():
#     """Check if the system is ready"""
#     try:
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         print("\n🔍 System Status Check:")
#         print("-" * 30)
#
#         if not index_path.exists():
#             print("❌ Data not processed yet")
#             print("   Run 'embed' command to process your CSV files")
#             return False
#
#         file_size = index_path.stat().st_size
#         print(f"✅ Data processed successfully")
#         print(f"   Index file size: {file_size:,} bytes")
#         print("   System ready for questions!")
#         return True
#
#     except ImportError:
#         print("❌ Configuration file not found")
#         print("   Check your app.configs module")
#         return False
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Main terminal interface loop"""
#     print("🚀 Starting FinBot - Your Friendly Cloud Cost Assistant")
#     print("=" * 60)
#
#     # Check system status
#     system_ready = check_system_status()
#
#     if not system_ready:
#         print("\n⚠️  System not ready! Please run 'embed' command first.")
#
#     show_help()
#
#     print("\n🗣️  Ready to help! Type your question or 'help' for assistance.")
#     print("💡 Now with intelligent response generation - no external AI needed!")
#
#     # Main interaction loop
#     while True:
#         try:
#             # Get user input with friendly prompt
#             user_input = input("\n💬 Ask FinBot> ").strip()
#
#             # Handle empty input
#             if not user_input:
#                 print("🤔 Please ask me a question about your cloud costs!")
#                 continue
#
#             # Handle commands
#             if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
#                 print("👋 Thanks for using FinBot! Have a great day!")
#                 break
#
#             elif user_input.lower() in ['help', '?', 'h']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() in ['examples', 'example', 'ex']:
#                 show_examples()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Processing your data... This might take a few minutes.")
#                 print("   ⏳ Analyzing CSV files and creating search index...")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"\n🎉 Success! Your data is now ready for questions!")
#                     print(f"   📊 Processed records:")
#                     print(f"   • Added: {stats['added_vectors']} new entries")
#                     print(f"   • Skipped: {stats['skipped_existing']} existing entries")
#                     print(f"   • Updated: {stats['updated_metadata']} metadata records")
#                     system_ready = True
#                     print("\n💡 Now you can start asking questions about your costs!")
#                 except Exception as e:
#                     print(f"❌ Processing failed: {e}")
#                     print("   Please check your CSV files and database connection.")
#                 continue
#
#             elif user_input.lower() in ['status', 'check']:
#                 check_system_status()
#                 continue
#
#             # Handle regular questions
#             if not system_ready:
#                 print("⚠️  I need to process your data first.")
#                 print("   Please run 'embed' command to get started.")
#                 continue
#
#             # Process the question and generate response
#             response_data = process_query(user_input)
#
#             if response_data:
#                 display_friendly_response(response_data)
#             else:
#                 print("😕 I couldn't find relevant information for your question.")
#                 print("💡 Try rephrasing your question or check if your data covers that time period.")
#                 print("   Example: 'What did we spend on storage in July 2025?'")
#
#         except KeyboardInterrupt:
#             print("\n\n👋 Thanks for using FinBot! Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Something went wrong: {e}")
#             print("💡 Please try rephrasing your question or check 'help' for examples.")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


# # !/usr/bin/env python3
# """
# Terminal-based RAG System Interface - With Smart Query Classification
# Run this script to interact with your FinOps RAG system via command line.
# """
#
# import os
# import sys
# import logging
# import re
# from pathlib import Path
# from collections import defaultdict
#
# # Add your app directory to Python path if needed
# # sys.path.insert(0, str(Path(__file__).parent))
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts import build_simple_prompt, get_human_friendly_examples
#
# # Configure logging to reduce noise in terminal
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
#
# def classify_query(question):
#     """Classify the type of user query"""
#     question_lower = question.lower().strip()
#
#     # Greeting patterns
#     greeting_patterns = [
#         r'^(hi+|hello|hey|good morning|good afternoon|good evening)$',
#         r'^(ram ram|namaste|namaskar)$',
#         r'^(hii+|hiii+|hiiii+)$'
#     ]
#
#     # Nonsensical/unclear patterns
#     unclear_patterns = [
#         r'^(what\??|huh\??|eh\??|\?\?+)$',
#         r'^(hmm+|um+|uh+)$',
#         r'^(\?+|\.+|\!+)$'
#     ]
#
#     # Financial/cost-related keywords
#     financial_keywords = [
#         'cost', 'price', 'spend', 'expense', 'bill', 'charge', 'money', 'dollar',
#         'service', 'storage', 'compute', 'database', 'ai', 'networking',
#         'invoice', 'month', '2025', 'total', 'how much', 'budget'
#     ]
#
#     # Check for greetings
#     for pattern in greeting_patterns:
#         if re.match(pattern, question_lower):
#             return 'greeting'
#
#     # Check for unclear/nonsensical queries
#     for pattern in unclear_patterns:
#         if re.match(pattern, question_lower):
#             return 'unclear'
#
#     # Check for financial keywords
#     has_financial_keywords = any(keyword in question_lower for keyword in financial_keywords)
#
#     # Check for date/time references
#     has_time_reference = bool(re.search(
#         r'(2025|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}-\d{2})',
#         question_lower))
#
#     # Financial query if it has financial keywords or time references with some context
#     if has_financial_keywords or (has_time_reference and len(question.split()) > 2):
#         return 'financial'
#
#     # Default to unclear if we can't classify
#     return 'unclear'
#
#
# def extract_service_filter(question):
#     """Extract specific service mentioned in the question"""
#     question_lower = question.lower()
#
#     services = {
#         'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
#         'compute': ['compute', 'server', 'vm', 'virtual machine', 'processing'],
#         'storage': ['storage', 'disk', 'file', 'backup'],
#         'database': ['database', 'db', 'data'],
#         'networking': ['network', 'networking', 'bandwidth', 'traffic']
#     }
#
#     for service, keywords in services.items():
#         if any(keyword in question_lower for keyword in keywords):
#             return service
#
#     return None
#
#
# def extract_time_filter(question):
#     """Extract specific time period mentioned in the question"""
#     # Look for year patterns
#     if 'year 2025' in question.lower() or '2025 year' in question.lower():
#         return 'year_2025'
#
#     # Look for specific months
#     month_match = re.search(r'2025-(\d{2})', question)
#     if month_match:
#         return f"2025-{month_match.group(1)}"
#
#     # Look for month names
#     months = {
#         'january': '2025-01', 'february': '2025-02', 'march': '2025-03',
#         'april': '2025-04', 'may': '2025-05', 'june': '2025-06',
#         'july': '2025-07', 'august': '2025-08', 'september': '2025-09',
#         'october': '2025-10', 'november': '2025-11', 'december': '2025-12'
#     }
#
#     for month_name, month_code in months.items():
#         if month_name in question.lower() and '2025' in question.lower():
#             return month_code
#
#     return None
#
#
# def handle_greeting():
#     """Handle greeting queries"""
#     greetings = [
#         "Hello! I'm FinBot, your cloud cost assistant. 😊",
#         "Hi there! I'm here to help you understand your cloud spending.",
#         "Namaste! I can help you analyze your cloud costs and expenses.",
#         "Hello! Ready to dive into your cloud financial data?"
#     ]
#
#     import random
#     greeting = random.choice(greetings)
#
#     return {
#         'type': 'greeting',
#         'response': f"{greeting} Ask me questions like:\n• 'What did we spend on AI services in 2025?'\n• 'Show me storage costs for July 2025'\n• 'Which service costs the most?'"
#     }
#
#
# def handle_unclear_query():
#     """Handle unclear or nonsensical queries"""
#     return {
#         'type': 'unclear',
#         'response': "I'm not sure what you're asking about. 🤔\n\nI can help you with questions about your cloud costs and spending. Try asking:\n• 'What did we spend on storage in July 2025?'\n• 'Show me total AI service costs'\n• 'Which service is most expensive?'\n\nType 'help' to see more examples!"
#     }
#
#
# def parse_billing_data(sources, service_filter=None, time_filter=None):
#     """Parse billing sources into structured data with filters"""
#     billing_data = []
#     resource_data = []
#
#     for source in sources:
#         snippet = source.get('snippet', '')
#         table_name = source.get('table_name', '')
#
#         if table_name == 'billing' and snippet:
#             # Parse billing information
#             billing_info = {}
#
#             # Extract month
#             month_match = re.search(r'2025-(\d{2})', snippet)
#             if month_match:
#                 month_num = month_match.group(1)
#                 billing_info['month_code'] = f"2025-{month_num}"
#
#             # Extract service
#             service_match = re.search(r'service (\w+)', snippet)
#             if service_match:
#                 billing_info['service'] = service_match.group(1).lower()
#
#             # Extract cost
#             cost_match = re.search(r'cost (\d+\.?\d*)', snippet)
#             if cost_match:
#                 try:
#                     billing_info['cost'] = float(cost_match.group(1))
#                 except:
#                     billing_info['cost'] = 0
#
#             # Apply filters
#             skip_record = False
#
#             # Service filter
#             if service_filter and billing_info.get('service'):
#                 if billing_info['service'].lower() != service_filter.lower():
#                     skip_record = True
#
#             # Time filter
#             if time_filter:
#                 if time_filter == 'year_2025':
#                     # Include all 2025 records
#                     if not billing_info.get('month_code', '').startswith('2025'):
#                         skip_record = True
#                 elif time_filter.startswith('2025-'):
#                     # Specific month
#                     if billing_info.get('month_code') != time_filter:
#                         skip_record = True
#
#             if not skip_record and billing_info:
#                 billing_data.append(billing_info)
#
#         elif table_name == 'resources' and snippet:
#             resource_data.append({'snippet': snippet})
#
#     return billing_data, resource_data
#
#
# def generate_financial_response(question, billing_data, resource_data, service_filter=None, time_filter=None):
#     """Generate a context-specific financial response"""
#     if not billing_data:
#         if service_filter and time_filter:
#             return f"I couldn't find any {service_filter} service charges for the specified time period. You might not have used {service_filter} services during that time, or the data might not be available in your records."
#         elif service_filter:
#             return f"I couldn't find any {service_filter} service charges in your records. You might not have used {service_filter} services, or they might be listed under a different name."
#         elif time_filter:
#             return f"I couldn't find any billing records for the specified time period. This might mean you didn't have any charges then, or the data might not be available."
#         else:
#             return "I couldn't find any relevant billing information for your question. Please make sure your data has been processed with the 'embed' command."
#
#     response_parts = []
#     total_cost = sum(b.get('cost', 0) for b in billing_data)
#
#     # Handle specific service queries
#     if service_filter:
#         service_name = service_filter.upper()
#         records_count = len(billing_data)
#
#         if time_filter == 'year_2025':
#             response_parts.append(
#                 f"For {service_name} services in 2025, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#
#             # Break down by months if multiple months
#             months = {}
#             for item in billing_data:
#                 month_code = item.get('month_code', 'Unknown')
#                 cost = item.get('cost', 0)
#                 if month_code in months:
#                     months[month_code] += cost
#                 else:
#                     months[month_code] = cost
#
#             if len(months) > 1:
#                 response_parts.append(f"This spending was spread across {len(months)} months:")
#                 for month_code, cost in sorted(months.items()):
#                     month_name = get_month_name(month_code)
#                     response_parts.append(f"• {month_name}: ${cost:,.2f}")
#
#         elif time_filter:
#             month_name = get_month_name(time_filter)
#             response_parts.append(
#                 f"For {service_name} services in {month_name}, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#         else:
#             response_parts.append(
#                 f"For {service_name} services, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#
#         # Add service explanation
#         service_descriptions = {
#             'ai': "AI services include machine learning models, language processing, and artificial intelligence capabilities that help automate and enhance your business processes.",
#             'compute': "Compute services include your servers, virtual machines, and processing power that run your applications and websites.",
#             'storage': "Storage services cover the cost of keeping your files, databases, backups, and data safely stored in the cloud.",
#             'database': "Database services handle storing, organizing, and managing your structured business data with high availability and security.",
#             'networking': "Networking services include data transfer, load balancing, and connectivity between your cloud resources."
#         }
#
#         if service_filter.lower() in service_descriptions:
#             response_parts.append(service_descriptions[service_filter.lower()])
#
#     # Handle time-specific queries without service filter
#     elif time_filter and not service_filter:
#         if time_filter == 'year_2025':
#             response_parts.append(
#                 f"For the year 2025, I found {len(billing_data)} transactions totaling ${total_cost:,.2f}.")
#         else:
#             month_name = get_month_name(time_filter)
#             response_parts.append(
#                 f"For {month_name}, I found {len(billing_data)} transactions totaling ${total_cost:,.2f}.")
#
#         # Break down by services
#         services = {}
#         for item in billing_data:
#             service = item.get('service', 'unknown')
#             cost = item.get('cost', 0)
#             if service in services:
#                 services[service] += cost
#             else:
#                 services[service] = cost
#
#         if len(services) > 1:
#             response_parts.append("Here's the breakdown by service:")
#             sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#             for service, cost in sorted_services:
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {service.upper()}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#     # General query handling
#     else:
#         response_parts.append(f"I found {len(billing_data)} billing transactions totaling ${total_cost:,.2f}.")
#
#         # Show service breakdown
#         services = {}
#         for item in billing_data:
#             service = item.get('service', 'unknown')
#             cost = item.get('cost', 0)
#             if service in services:
#                 services[service] += cost
#             else:
#                 services[service] = cost
#
#         if services:
#             sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#             response_parts.append("Your spending breakdown by service:")
#             for service, cost in sorted_services[:5]:  # Top 5 services
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {service.upper()}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#     return " ".join(response_parts)
#
#
# def get_month_name(month_code):
#     """Convert month code to readable name"""
#     month_names = {
#         '2025-01': 'January 2025', '2025-02': 'February 2025', '2025-03': 'March 2025',
#         '2025-04': 'April 2025', '2025-05': 'May 2025', '2025-06': 'June 2025',
#         '2025-07': 'July 2025', '2025-08': 'August 2025', '2025-09': 'September 2025',
#         '2025-10': 'October 2025', '2025-11': 'November 2025', '2025-12': 'December 2025'
#     }
#     return month_names.get(month_code, month_code)
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question with smart classification"""
#
#     # First classify the query
#     query_type = classify_query(question)
#
#     # Handle non-financial queries
#     if query_type == 'greeting':
#         return handle_greeting()
#
#     if query_type == 'unclear':
#         return handle_unclear_query()
#
#     # Only search financial data for financial queries
#     if query_type != 'financial':
#         return handle_unclear_query()
#
#     print(f"\n🔍 Searching through your financial records...")
#
#     # Extract filters from the question
#     service_filter = extract_service_filter(question)
#     time_filter = extract_time_filter(question)
#
#     # Get relevant context
#     results = query_knn(question, k=k)
#
#     if not results:
#         return {
#             'type': 'no_results',
#             'response': "I couldn't find any relevant financial data for your question. Make sure you've run the 'embed' command to process your CSV files."
#         }
#
#     # Remove duplicates and None values
#     unique_results = []
#     seen_snippets = set()
#     for result in results:
#         snippet = result.get('snippet')
#         if snippet and snippet.strip() and snippet not in seen_snippets:
#             if snippet.strip() != 'None' and len(snippet.strip()) > 5:
#                 unique_results.append(result)
#                 seen_snippets.add(snippet)
#
#     if not unique_results:
#         return {
#             'type': 'no_useful_results',
#             'response': "Found some records but they don't contain useful financial information. Try rephrasing your question with specific services or time periods."
#         }
#
#     # Parse the data with filters
#     billing_data, resource_data = parse_billing_data(unique_results, service_filter, time_filter)
#
#     # Generate context-specific response
#     financial_response = generate_financial_response(question, billing_data, resource_data, service_filter, time_filter)
#
#     print(f"✅ Found {len(unique_results)} relevant records")
#     return {
#         'type': 'financial',
#         'question': question,
#         'response': financial_response,
#         'billing_data': billing_data,
#         'resource_data': resource_data,
#         'sources': unique_results,
#         'filters': {
#             'service': service_filter,
#             'time': time_filter
#         }
#     }
#
#
# def display_response(response_data):
#     """Display the appropriate response based on type"""
#     if not response_data:
#         return
#
#     response_type = response_data.get('type')
#
#     # Handle non-financial responses simply
#     if response_type in ['greeting', 'unclear', 'no_results', 'no_useful_results']:
#         print(f"\n💬 {response_data['response']}")
#         return
#
#     # Handle financial responses with full formatting
#     print("\n" + "=" * 70)
#     print("💼 FinBot - Your Cloud Cost Assistant")
#     print("=" * 70)
#
#     print(f"\n🎯 Your Question: {response_data['question']}")
#
#     # Show applied filters
#     filters = response_data.get('filters', {})
#     if filters.get('service') or filters.get('time'):
#         print(f"\n🔍 Applied Filters:")
#         if filters.get('service'):
#             print(f"   • Service: {filters['service'].upper()}")
#         if filters.get('time'):
#             if filters['time'] == 'year_2025':
#                 print(f"   • Time Period: Year 2025")
#             else:
#                 print(f"   • Time Period: {get_month_name(filters['time'])}")
#
#     print(f"\n🤖 FinBot Analysis:")
#     print("-" * 40)
#     print(response_data['response'])
#
#     # Show supporting data if available
#     if response_data.get('billing_data'):
#         print(f"\n📊 Supporting Data:")
#         print("-" * 25)
#         for i, billing in enumerate(response_data['billing_data'][:5], 1):
#             month_code = billing.get('month_code', 'Unknown')
#             month_name = get_month_name(month_code)
#             service = billing.get('service', 'Unknown').upper()
#             cost = billing.get('cost', 0)
#             print(f"   {i}. {month_name}: {service} - ${cost:,.2f}")
#
#     print(f"\n📈 Data Summary: Analyzed {len(response_data.get('sources', []))} records from your financial database")
#
#
# def show_help():
#     """Display help information"""
#     help_text = """
# 🚀 FinBot - Smart Cloud Cost Assistant
# =====================================
#
# I can help you understand your cloud spending! I'm smart enough to know when
# you're greeting me vs asking about costs.
#
# 💬 COMMANDS:
# • Ask financial questions in plain English
# • 'help' - Show this help menu
# • 'embed' - Process your CSV data (do this first!)
# • 'status' - Check if system is ready
# • 'examples' - Show example questions
# • 'quit' or 'exit' - Leave the program
#
# 🎯 EXAMPLE QUESTIONS:
# • "What did we spend on AI services in 2025?"
# • "Show me storage costs for July 2025"
# • "Get total cost of Compute service in year 2025"
# • "How much did we spend in September 2025?"
# • "Which service costs the most?"
#
# 💡 GREETINGS & CASUAL CHAT:
# • "Hi", "Hello", "Ram Ram" - I'll greet you back!
# • I won't search financial data for casual conversation
#
# 🔧 FIRST TIME SETUP:
# 1. Run: embed
# 2. Wait for processing to complete
# 3. Start asking about your costs!
# """
#     print(help_text)
#
#
# def show_examples():
#     """Show example questions"""
#     print("\n🎯 Example Financial Questions:")
#     print("=" * 50)
#
#     examples = [
#         "Get total cost of AI service used in year 2025",
#         "What did we spend on storage in July 2025?",
#         "How much did compute services cost in 2025?",
#         "Show me expenses for September 2025",
#         "Which service is most expensive?"
#     ]
#
#     for i, example in enumerate(examples, 1):
#         print(f"{i}. {example}")
#
#     print(f"\n💡 I can also handle greetings like 'Hi' or 'Hello' without searching data!")
#
#
# def check_system_status():
#     """Check if the system is ready"""
#     try:
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         print("\n🔍 System Status Check:")
#         print("-" * 30)
#
#         if not index_path.exists():
#             print("❌ Data not processed yet")
#             print("   Run 'embed' command to process your CSV files")
#             return False
#
#         file_size = index_path.stat().st_size
#         print(f"✅ Data processed successfully")
#         print(f"   Index file size: {file_size:,} bytes")
#         print("   System ready for questions!")
#         return True
#
#     except ImportError:
#         print("❌ Configuration file not found")
#         return False
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Main terminal interface loop"""
#     print("🚀 Starting FinBot - Smart Cloud Cost Assistant")
#     print("=" * 60)
#
#     # Check system status
#     system_ready = check_system_status()
#
#     if not system_ready:
#         print("\n⚠️  System not ready! Please run 'embed' command first.")
#
#     show_help()
#
#     print("\n🗣️  Ready to help! I can handle both greetings and financial questions.")
#     print("💡 Try saying 'Hi' or asking about your cloud costs!")
#
#     # Main interaction loop
#     while True:
#         try:
#             # Get user input
#             user_input = input("\n💬 Ask FinBot> ").strip()
#
#             if not user_input:
#                 print("🤔 Please ask me something!")
#                 continue
#
#             # Handle system commands
#             if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
#                 print("👋 Thanks for using FinBot! Have a great day!")
#                 break
#
#             elif user_input.lower() in ['help', '?', 'h']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() in ['examples', 'example', 'ex']:
#                 show_examples()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Processing your data...")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"\n🎉 Success! Processed {stats['added_vectors']} new records")
#                     system_ready = True
#                 except Exception as e:
#                     print(f"❌ Processing failed: {e}")
#                 continue
#
#             elif user_input.lower() in ['status', 'check']:
#                 check_system_status()
#                 continue
#
#             # Process the query with smart classification
#             response_data = process_query(user_input)
#
#             # For financial queries, check if system is ready
#             if response_data.get('type') == 'financial' and not system_ready:
#                 print("⚠️  I need to process your data first. Run 'embed' command to get started.")
#                 continue
#
#             # Display the response
#             display_response(response_data)
#
#         except KeyboardInterrupt:
#             print("\n\n👋 Thanks for using FinBot! Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Something went wrong: {e}")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


# # !/usr/bin/env python3
# """
# Terminal-based RAG System Interface - With Comprehensive Service Listing
# """
#
# import os
# import sys
# import logging
# import re
# from pathlib import Path
# from collections import defaultdict
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts import build_simple_prompt, get_human_friendly_examples
#
# # Add database imports
# from sqlalchemy import select, distinct
# from app.db.base import SessionLocal
# from app.db import models
#
# # Configure logging to reduce noise in terminal
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
#
# def get_all_services_from_db():
#     """Get all unique services directly from the database"""
#     try:
#         session = SessionLocal()
#         # Get all unique services from billing table
#         services_result = session.execute(
#             select(distinct(models.Billing.service))
#             .where(models.Billing.service.isnot(None))
#         ).scalars().all()
#
#         session.close()
#
#         # Filter out None values and empty strings
#         services = [service for service in services_result if service and service.strip()]
#         return sorted(services)
#     except Exception as e:
#         logger.error(f"Error getting services from database: {e}")
#         return []
#
#
# def get_all_months_from_db():
#     """Get all unique months from the database"""
#     try:
#         session = SessionLocal()
#         months_result = session.execute(
#             select(distinct(models.Billing.invoice_month))
#             .where(models.Billing.invoice_month.isnot(None))
#         ).scalars().all()
#
#         session.close()
#
#         months = [month for month in months_result if month and month.strip()]
#         return sorted(months)
#     except Exception as e:
#         logger.error(f"Error getting months from database: {e}")
#         return []
#
#
# def get_comprehensive_service_summary():
#     """Get comprehensive service summary from database"""
#     try:
#         session = SessionLocal()
#
#         # Get billing data grouped by service
#         billing_rows = session.execute(select(models.Billing)).scalars().all()
#         session.close()
#
#         service_data = {}
#         total_cost = 0
#
#         for row in billing_rows:
#             service = getattr(row, 'service', None)
#             cost = getattr(row, 'cost', 0)
#             month = getattr(row, 'invoice_month', None)
#
#             if service and cost is not None:
#                 if service not in service_data:
#                     service_data[service] = {
#                         'total_cost': 0,
#                         'transaction_count': 0,
#                         'months': set()
#                     }
#
#                 service_data[service]['total_cost'] += float(cost)
#                 service_data[service]['transaction_count'] += 1
#                 if month:
#                     service_data[service]['months'].add(month)
#                 total_cost += float(cost)
#
#         return service_data, total_cost
#     except Exception as e:
#         logger.error(f"Error getting service summary: {e}")
#         return {}, 0
#
#
# def classify_query(question):
#     """Classify the type of user query"""
#     question_lower = question.lower().strip()
#
#     # Greeting patterns
#     greeting_patterns = [
#         r'^(hi+|hello|hey|good morning|good afternoon|good evening)$',
#         r'^(ram ram|namaste|namaskar)$',
#         r'^(hii+|hiii+|hiiii+)$'
#     ]
#
#     # Service listing patterns
#     service_list_patterns = [
#         r'list.*services?',
#         r'show.*services?',
#         r'all.*services?',
#         r'what.*services?',
#         r'services?.*we.*use',
#         r'services?.*names?',
#         r'services?.*available'
#     ]
#
#     # Nonsensical/unclear patterns
#     unclear_patterns = [
#         r'^(what\??|huh\??|eh\??|\?\?+)$',
#         r'^(hmm+|um+|uh+)$',
#         r'^(\?+|\.+|\!+)$'
#     ]
#
#     # Financial/cost-related keywords
#     financial_keywords = [
#         'cost', 'price', 'spend', 'expense', 'bill', 'charge', 'money', 'dollar',
#         'invoice', 'month', '2025', 'total', 'how much', 'budget'
#     ]
#
#     # Check for greetings
#     for pattern in greeting_patterns:
#         if re.match(pattern, question_lower):
#             return 'greeting'
#
#     # Check for service listing requests
#     for pattern in service_list_patterns:
#         if re.search(pattern, question_lower):
#             return 'service_list'
#
#     # Check for unclear/nonsensical queries
#     for pattern in unclear_patterns:
#         if re.match(pattern, question_lower):
#             return 'unclear'
#
#     # Check for financial keywords
#     has_financial_keywords = any(keyword in question_lower for keyword in financial_keywords)
#     has_time_reference = bool(re.search(
#         r'(2025|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}-\d{2})',
#         question_lower))
#
#     # Financial query if it has financial keywords or time references with context
#     if has_financial_keywords or (has_time_reference and len(question.split()) > 2):
#         return 'financial'
#
#     return 'unclear'
#
#
# def handle_service_list_query(question):
#     """Handle requests for listing services"""
#     question_lower = question.lower()
#
#     # Check if user wants just names (no costs)
#     wants_names_only = any(phrase in question_lower for phrase in [
#         'just names', 'only names', 'service names', 'name not', 'not cost', 'not percentage',
#         'without cost', 'without percentage', 'names only', 'list names'
#     ])
#
#     if wants_names_only:
#         # Get all services directly from database
#         services = get_all_services_from_db()
#
#         if not services:
#             return {
#                 'type': 'service_list',
#                 'response': "I couldn't find any services in your database. Make sure your data has been processed with the 'embed' command."
#             }
#
#         response = f"Here are all the cloud services you've used:\n\n"
#         for i, service in enumerate(services, 1):
#             response += f"{i}. {service.upper()}\n"
#
#         response += f"\nTotal: {len(services)} different services found in your records."
#
#         return {
#             'type': 'service_list',
#             'response': response,
#             'services': services
#         }
#
#     else:
#         # Get comprehensive service summary
#         service_data, total_cost = get_comprehensive_service_summary()
#
#         if not service_data:
#             return {
#                 'type': 'service_list',
#                 'response': "I couldn't find any service data in your database."
#             }
#
#         # Sort services by total cost (descending)
#         sorted_services = sorted(service_data.items(), key=lambda x: x[1]['total_cost'], reverse=True)
#
#         response = f"Here are all the cloud services you've used with their details:\n\n"
#
#         for i, (service, data) in enumerate(sorted_services, 1):
#             percentage = (data['total_cost'] / total_cost) * 100 if total_cost > 0 else 0
#             months_count = len(data['months'])
#
#             response += f"{i}. {service.upper()}\n"
#             response += f"   • Total spent: ${data['total_cost']:,.2f} ({percentage:.1f}% of all spending)\n"
#             response += f"   • Transactions: {data['transaction_count']}\n"
#             response += f"   • Active in {months_count} month{'s' if months_count != 1 else ''}\n\n"
#
#         response += f"Summary: {len(sorted_services)} different services, ${total_cost:,.2f} total spending"
#
#         return {
#             'type': 'service_list_detailed',
#             'response': response,
#             'service_data': service_data,
#             'total_cost': total_cost
#         }
#
#
# def extract_service_filter(question):
#     """Extract specific service mentioned in the question"""
#     question_lower = question.lower()
#
#     services = {
#         'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
#         'compute': ['compute', 'server', 'vm', 'virtual machine', 'processing'],
#         'storage': ['storage', 'disk', 'file', 'backup'],
#         'database': ['database', 'db', 'data'],
#         'networking': ['network', 'networking', 'bandwidth', 'traffic']
#     }
#
#     for service, keywords in services.items():
#         if any(keyword in question_lower for keyword in keywords):
#             return service
#
#     return None
#
#
# def extract_time_filter(question):
#     """Extract specific time period mentioned in the question"""
#     # Look for year patterns
#     if 'year 2025' in question.lower() or '2025 year' in question.lower():
#         return 'year_2025'
#
#     # Look for specific months
#     month_match = re.search(r'2025-(\d{2})', question)
#     if month_match:
#         return f"2025-{month_match.group(1)}"
#
#     # Look for month names
#     months = {
#         'january': '2025-01', 'february': '2025-02', 'march': '2025-03',
#         'april': '2025-04', 'may': '2025-05', 'june': '2025-06',
#         'july': '2025-07', 'august': '2025-08', 'september': '2025-09',
#         'october': '2025-10', 'november': '2025-11', 'december': '2025-12'
#     }
#
#     for month_name, month_code in months.items():
#         if month_name in question.lower() and '2025' in question.lower():
#             return month_code
#
#     return None
#
#
# def handle_greeting():
#     """Handle greeting queries"""
#     greetings = [
#         "Hello! I'm FinBot, your cloud cost assistant. 😊",
#         "Hi there! I'm here to help you understand your cloud spending.",
#         "Namaste! I can help you analyze your cloud costs and expenses.",
#         "Hello! Ready to dive into your cloud financial data?"
#     ]
#
#     import random
#     greeting = random.choice(greetings)
#
#     return {
#         'type': 'greeting',
#         'response': f"{greeting} Ask me questions like:\n• 'What did we spend on AI services in 2025?'\n• 'Show me storage costs for July 2025'\n• 'List all services' (for service names only)"
#     }
#
#
# def handle_unclear_query():
#     """Handle unclear or nonsensical queries"""
#     return {
#         'type': 'unclear',
#         'response': "I'm not sure what you're asking about. 🤔\n\nI can help you with:\n• Cloud cost questions: 'What did we spend on storage in July 2025?'\n• Service listings: 'List all services' or 'Show all service names'\n• Financial summaries: 'Which service costs the most?'\n\nType 'help' to see more examples!"
#     }
#
#
# def parse_billing_data(sources, service_filter=None, time_filter=None):
#     """Parse billing sources into structured data with filters"""
#     billing_data = []
#     resource_data = []
#
#     for source in sources:
#         snippet = source.get('snippet', '')
#         table_name = source.get('table_name', '')
#
#         if table_name == 'billing' and snippet:
#             # Parse billing information
#             billing_info = {}
#
#             # Extract month
#             month_match = re.search(r'2025-(\d{2})', snippet)
#             if month_match:
#                 month_num = month_match.group(1)
#                 billing_info['month_code'] = f"2025-{month_num}"
#
#             # Extract service
#             service_match = re.search(r'service (\w+)', snippet)
#             if service_match:
#                 billing_info['service'] = service_match.group(1).lower()
#
#             # Extract cost
#             cost_match = re.search(r'cost (\d+\.?\d*)', snippet)
#             if cost_match:
#                 try:
#                     billing_info['cost'] = float(cost_match.group(1))
#                 except:
#                     billing_info['cost'] = 0
#
#             # Apply filters
#             skip_record = False
#
#             # Service filter
#             if service_filter and billing_info.get('service'):
#                 if billing_info['service'].lower() != service_filter.lower():
#                     skip_record = True
#
#             # Time filter
#             if time_filter:
#                 if time_filter == 'year_2025':
#                     # Include all 2025 records
#                     if not billing_info.get('month_code', '').startswith('2025'):
#                         skip_record = True
#                 elif time_filter.startswith('2025-'):
#                     # Specific month
#                     if billing_info.get('month_code') != time_filter:
#                         skip_record = True
#
#             if not skip_record and billing_info:
#                 billing_data.append(billing_info)
#
#         elif table_name == 'resources' and snippet:
#             resource_data.append({'snippet': snippet})
#
#     return billing_data, resource_data
#
#
# def generate_financial_response(question, billing_data, resource_data, service_filter=None, time_filter=None):
#     """Generate a context-specific financial response"""
#     if not billing_data:
#         if service_filter and time_filter:
#             return f"I couldn't find any {service_filter} service charges for the specified time period. You might not have used {service_filter} services during that time, or the data might not be available in your records."
#         elif service_filter:
#             return f"I couldn't find any {service_filter} service charges in your records. You might not have used {service_filter} services, or they might be listed under a different name."
#         elif time_filter:
#             return f"I couldn't find any billing records for the specified time period. This might mean you didn't have any charges then, or the data might not be available."
#         else:
#             return "I couldn't find any relevant billing information for your question. Please make sure your data has been processed with the 'embed' command."
#
#     response_parts = []
#     total_cost = sum(b.get('cost', 0) for b in billing_data)
#
#     # Handle specific service queries
#     if service_filter:
#         service_name = service_filter.upper()
#         records_count = len(billing_data)
#
#         if time_filter == 'year_2025':
#             response_parts.append(
#                 f"For {service_name} services in 2025, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#
#             # Break down by months if multiple months
#             months = {}
#             for item in billing_data:
#                 month_code = item.get('month_code', 'Unknown')
#                 cost = item.get('cost', 0)
#                 if month_code in months:
#                     months[month_code] += cost
#                 else:
#                     months[month_code] = cost
#
#             if len(months) > 1:
#                 response_parts.append(f"This spending was spread across {len(months)} months:")
#                 for month_code, cost in sorted(months.items()):
#                     month_name = get_month_name(month_code)
#                     response_parts.append(f"• {month_name}: ${cost:,.2f}")
#
#         elif time_filter:
#             month_name = get_month_name(time_filter)
#             response_parts.append(
#                 f"For {service_name} services in {month_name}, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#         else:
#             response_parts.append(
#                 f"For {service_name} services, I found {records_count} transaction{'s' if records_count != 1 else ''} totaling ${total_cost:,.2f}.")
#
#         # Add service explanation
#         service_descriptions = {
#             'ai': "AI services include machine learning models, language processing, and artificial intelligence capabilities that help automate and enhance your business processes.",
#             'compute': "Compute services include your servers, virtual machines, and processing power that run your applications and websites.",
#             'storage': "Storage services cover the cost of keeping your files, databases, backups, and data safely stored in the cloud.",
#             'database': "Database services handle storing, organizing, and managing your structured business data with high availability and security.",
#             'networking': "Networking services include data transfer, load balancing, and connectivity between your cloud resources."
#         }
#
#         if service_filter.lower() in service_descriptions:
#             response_parts.append(service_descriptions[service_filter.lower()])
#
#     # Handle time-specific queries without service filter
#     elif time_filter and not service_filter:
#         if time_filter == 'year_2025':
#             response_parts.append(
#                 f"For the year 2025, I found {len(billing_data)} transactions totaling ${total_cost:,.2f}.")
#         else:
#             month_name = get_month_name(time_filter)
#             response_parts.append(
#                 f"For {month_name}, I found {len(billing_data)} transactions totaling ${total_cost:,.2f}.")
#
#         # Break down by services
#         services = {}
#         for item in billing_data:
#             service = item.get('service', 'unknown')
#             cost = item.get('cost', 0)
#             if service in services:
#                 services[service] += cost
#             else:
#                 services[service] = cost
#
#         if len(services) > 1:
#             response_parts.append("Here's the breakdown by service:")
#             sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#             for service, cost in sorted_services:
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {service.upper()}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#     # General query handling
#     else:
#         response_parts.append(f"I found {len(billing_data)} billing transactions totaling ${total_cost:,.2f}.")
#
#         # Show service breakdown
#         services = {}
#         for item in billing_data:
#             service = item.get('service', 'unknown')
#             cost = item.get('cost', 0)
#             if service in services:
#                 services[service] += cost
#             else:
#                 services[service] = cost
#
#         if services:
#             sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#             response_parts.append("Your spending breakdown by service:")
#             for service, cost in sorted_services[:5]:  # Top 5 services
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {service.upper()}: ${cost:,.2f} ({percentage:.1f}% of total)")
#
#     return " ".join(response_parts)
#
#
# def get_month_name(month_code):
#     """Convert month code to readable name"""
#     month_names = {
#         '2025-01': 'January 2025', '2025-02': 'February 2025', '2025-03': 'March 2025',
#         '2025-04': 'April 2025', '2025-05': 'May 2025', '2025-06': 'June 2025',
#         '2025-07': 'July 2025', '2025-08': 'August 2025', '2025-09': 'September 2025',
#         '2025-10': 'October 2025', '2025-11': 'November 2025', '2025-12': 'December 2025'
#     }
#     return month_names.get(month_code, month_code)
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question with smart classification"""
#
#     # First classify the query
#     query_type = classify_query(question)
#
#     # Handle non-financial queries
#     if query_type == 'greeting':
#         return handle_greeting()
#
#     if query_type == 'unclear':
#         return handle_unclear_query()
#
#     # Handle service listing queries
#     if query_type == 'service_list':
#         return handle_service_list_query(question)
#
#     # Only search financial data for financial queries
#     if query_type != 'financial':
#         return handle_unclear_query()
#
#     print(f"\n🔍 Searching through your financial records...")
#
#     # Extract filters from the question
#     service_filter = extract_service_filter(question)
#     time_filter = extract_time_filter(question)
#
#     # Get relevant context
#     results = query_knn(question, k=k)
#
#     if not results:
#         return {
#             'type': 'no_results',
#             'response': "I couldn't find any relevant financial data for your question. Make sure you've run the 'embed' command to process your CSV files."
#         }
#
#     # Remove duplicates and None values
#     unique_results = []
#     seen_snippets = set()
#     for result in results:
#         snippet = result.get('snippet')
#         if snippet and snippet.strip() and snippet not in seen_snippets:
#             if snippet.strip() != 'None' and len(snippet.strip()) > 5:
#                 unique_results.append(result)
#                 seen_snippets.add(snippet)
#
#     if not unique_results:
#         return {
#             'type': 'no_useful_results',
#             'response': "Found some records but they don't contain useful financial information. Try rephrasing your question with specific services or time periods."
#         }
#
#     # Parse the data with filters
#     billing_data, resource_data = parse_billing_data(unique_results, service_filter, time_filter)
#
#     # Generate context-specific response
#     financial_response = generate_financial_response(question, billing_data, resource_data, service_filter, time_filter)
#
#     print(f"✅ Found {len(unique_results)} relevant records")
#     return {
#         'type': 'financial',
#         'question': question,
#         'response': financial_response,
#         'billing_data': billing_data,
#         'resource_data': resource_data,
#         'sources': unique_results,
#         'filters': {
#             'service': service_filter,
#             'time': time_filter
#         }
#     }
#
#
# def display_response(response_data):
#     """Display the appropriate response based on type"""
#     if not response_data:
#         return
#
#     response_type = response_data.get('type')
#
#     # Handle simple responses (greetings, unclear, service lists)
#     if response_type in ['greeting', 'unclear', 'no_results', 'no_useful_results', 'service_list']:
#         print(f"\n💬 {response_data['response']}")
#         return
#
#     # Handle detailed service list
#     if response_type == 'service_list_detailed':
#         print(f"\n📋 {response_data['response']}")
#         return
#
#     # Handle financial responses with full formatting
#     print("\n" + "=" * 70)
#     print("💼 FinBot - Your Cloud Cost Assistant")
#     print("=" * 70)
#
#     print(f"\n🎯 Your Question: {response_data['question']}")
#
#     # Show applied filters
#     filters = response_data.get('filters', {})
#     if filters.get('service') or filters.get('time'):
#         print(f"\n🔍 Applied Filters:")
#         if filters.get('service'):
#             print(f"   • Service: {filters['service'].upper()}")
#         if filters.get('time'):
#             if filters['time'] == 'year_2025':
#                 print(f"   • Time Period: Year 2025")
#             else:
#                 print(f"   • Time Period: {get_month_name(filters['time'])}")
#
#     print(f"\n🤖 FinBot Analysis:")
#     print("-" * 40)
#     print(response_data['response'])
#
#     # Show supporting data if available
#     if response_data.get('billing_data'):
#         print(f"\n📊 Supporting Data:")
#         print("-" * 25)
#         for i, billing in enumerate(response_data['billing_data'][:5], 1):
#             month_code = billing.get('month_code', 'Unknown')
#             month_name = get_month_name(month_code)
#             service = billing.get('service', 'Unknown').upper()
#             cost = billing.get('cost', 0)
#             print(f"   {i}. {month_name}: {service} - ${cost:,.2f}")
#
#     print(f"\n📈 Data Summary: Analyzed {len(response_data.get('sources', []))} records from your financial database")
#
#
# def show_help():
#     """Display help information"""
#     help_text = """
# 🚀 FinBot - Smart Cloud Cost Assistant
# =====================================
#
# I can help you understand your cloud spending! I'm smart enough to know when
# you're greeting me vs asking about costs vs requesting service lists.
#
# 💬 COMMANDS:
# • Ask financial questions in plain English
# • 'help' - Show this help menu
# • 'embed' - Process your CSV data (do this first!)
# • 'status' - Check if system is ready
# • 'examples' - Show example questions
# • 'quit' or 'exit' - Leave the program
#
# 🎯 FINANCIAL QUESTIONS:
# • "What did we spend on AI services in 2025?"
# • "Show me storage costs for July 2025"
# • "Get total cost of Compute service in year 2025"
# • "How much did we spend in September 2025?"
#
# 📋 SERVICE LISTING:
# • "List all services" - Shows services with costs & details
# • "List service names only" - Shows just the service names
# • "Show all services we used" - Comprehensive service breakdown
#
# 💡 GREETINGS & CASUAL CHAT:
# • "Hi", "Hello", "Ram Ram" - I'll greet you back!
# • I won't search financial data for casual conversation
#
# 🔧 FIRST TIME SETUP:
# 1. Run: embed
# 2. Wait for processing to complete
# 3. Start asking about your costs!
# """
#     print(help_text)
#
#
# def show_examples():
#     """Show example questions"""
#     print("\n🎯 Example Questions:")
#     print("=" * 50)
#
#     print("💰 Financial Questions:")
#     financial_examples = [
#         "Get total cost of AI service used in year 2025",
#         "What did we spend on storage in July 2025?",
#         "How much did compute services cost in 2025?",
#         "Show me expenses for September 2025"
#     ]
#
#     for i, example in enumerate(financial_examples, 1):
#         print(f"   {i}. {example}")
#
#     print(f"\n📋 Service Listing:")
#     service_examples = [
#         "List all services (shows costs and details)",
#         "List service names only (no costs or percentages)",
#         "Show all services we used",
#         "What services are available?"
#     ]
#
#     for i, example in enumerate(service_examples, 1):
#         print(f"   {i}. {example}")
#
#     print(f"\n💡 I can also handle greetings like 'Hi' without searching data!")
#
#
# def check_system_status():
#     """Check if the system is ready"""
#     try:
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         print("\n🔍 System Status Check:")
#         print("-" * 30)
#
#         if not index_path.exists():
#             print("❌ Data not processed yet")
#             print("   Run 'embed' command to process your CSV files")
#             return False
#
#         file_size = index_path.stat().st_size
#         print(f"✅ Data processed successfully")
#         print(f"   Index file size: {file_size:,} bytes")
#
#         # Also check database connectivity
#         services = get_all_services_from_db()
#         months = get_all_months_from_db()
#         print(f"   Services in database: {len(services)}")
#         print(f"   Months in database: {len(months)}")
#         print("   System ready for questions!")
#         return True
#
#     except ImportError:
#         print("❌ Configuration file not found")
#         return False
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Main terminal interface loop"""
#     print("🚀 Starting FinBot - Smart Cloud Cost Assistant")
#     print("=" * 60)
#
#     # Check system status
#     system_ready = check_system_status()
#
#     if not system_ready:
#         print("\n⚠️  System not ready! Please run 'embed' command first.")
#
#     show_help()
#
#     print("\n🗣️  Ready to help! I can handle greetings, financial questions, and service listings.")
#     print("💡 Try: 'Hi', 'List service names only', or 'What did we spend in July 2025?'")
#
#     # Main interaction loop
#     while True:
#         try:
#             # Get user input
#             user_input = input("\n💬 Ask FinBot> ").strip()
#
#             if not user_input:
#                 print("🤔 Please ask me something!")
#                 continue
#
#             # Handle system commands
#             if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
#                 print("👋 Thanks for using FinBot! Have a great day!")
#                 break
#
#             elif user_input.lower() in ['help', '?', 'h']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() in ['examples', 'example', 'ex']:
#                 show_examples()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Processing your data...")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"\n🎉 Success! Processed {stats['added_vectors']} new records")
#                     system_ready = True
#                 except Exception as e:
#                     print(f"❌ Processing failed: {e}")
#                 continue
#
#             elif user_input.lower() in ['status', 'check']:
#                 check_system_status()
#                 continue
#
#             # Process the query with smart classification
#             response_data = process_query(user_input)
#
#             # For financial queries, check if system is ready
#             if response_data.get('type') == 'financial' and not system_ready:
#                 print("⚠️  I need to process your data first. Run 'embed' command to get started.")
#                 continue
#
#             # Display the response
#             display_response(response_data)
#
#         except KeyboardInterrupt:
#             print("\n\n👋 Thanks for using FinBot! Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Something went wrong: {e}")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


# # !/usr/bin/env python3
# """
# Enhanced Terminal RAG System - With Comprehensive Query Support
# """
#
# import os
# import sys
# import logging
# import re
# from pathlib import Path
# from collections import defaultdict
#
# # Import your existing modules
# from app.services.embedder import query_knn, embed_all_and_store
# # from backend.prompts import build_simple_prompt, get_human_friendly_examples
# from backend.prompts import build_simple_prompt, get_enhanced_examples
#
#
# # Add database imports
# from sqlalchemy import select, distinct, func
# from app.db.base import SessionLocal
# from app.db import models
#
# # Configure logging to reduce noise in terminal
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
#
# def get_comprehensive_billing_data(filters=None):
#     """Get comprehensive billing data from database with filters"""
#     try:
#         session = SessionLocal()
#         query = select(models.Billing)
#
#         if filters:
#             if filters.get('service'):
#                 query = query.where(models.Billing.service.ilike(f"%{filters['service']}%"))
#             if filters.get('account_id'):
#                 query = query.where(models.Billing.account_id == filters['account_id'])
#             if filters.get('resource_id'):
#                 query = query.where(models.Billing.resource_id == filters['resource_id'])
#             if filters.get('month'):
#                 query = query.where(models.Billing.invoice_month == filters['month'])
#             if filters.get('year'):
#                 query = query.where(models.Billing.invoice_month.like(f"{filters['year']}%"))
#
#         billing_rows = session.execute(query).scalars().all()
#         session.close()
#
#         # Convert to dictionary format
#         billing_data = []
#         for row in billing_rows:
#             billing_data.append({
#                 'invoice_month': getattr(row, 'invoice_month', ''),
#                 'account_id': getattr(row, 'account_id', ''),
#                 'subscription': getattr(row, 'subscription', ''),
#                 'service': getattr(row, 'service', ''),
#                 'resource_group': getattr(row, 'resource_group', ''),
#                 'resource_id': getattr(row, 'resource_id', ''),
#                 'region': getattr(row, 'region', ''),
#                 'usage_qty': getattr(row, 'usage_qty', 0),
#                 'unit_cost': getattr(row, 'unit_cost', 0),
#                 'cost': getattr(row, 'cost', 0)
#             })
#
#         return billing_data
#     except Exception as e:
#         logger.error(f"Error getting billing data: {e}")
#         return []
#
#
# def classify_query(question):
#     """Enhanced query classification with more patterns"""
#     question_lower = question.lower().strip()
#
#     # Greeting patterns
#     greeting_patterns = [
#         r'^(hi+|hello|hey|good morning|good afternoon|good evening)$',
#         r'^(ram ram|namaste|namaskar)$',
#         r'^(hii+|hiii+|hiiii+)$'
#     ]
#
#     # Account-specific patterns
#     account_patterns = [
#         r'account.*acct-[a-f0-9]+',
#         r'acct-[a-f0-9]+.*details',
#         r'acct-[a-f0-9]+.*cost',
#         r'acct-[a-f0-9]+.*service',
#         r'how.*many.*services.*account',
#         r'account.*spending',
#         r'account.*breakdown'
#     ]
#
#     # Resource-specific patterns
#     resource_patterns = [
#         r'resource.*res-[a-f0-9]+',
#         r'res-[a-f0-9]+.*service',
#         r'res-[a-f0-9]+.*cost',
#         r'res-[a-f0-9]+.*belong',
#         r'resource.*belong.*service'
#     ]
#
#     # Service listing patterns
#     service_list_patterns = [
#         r'list.*services?',
#         r'show.*services?',
#         r'all.*services?',
#         r'what.*services?',
#         r'services?.*we.*use',
#         r'services?.*names?',
#         r'services?.*available'
#     ]
#
#     # Monthly breakdown patterns
#     monthly_breakdown_patterns = [
#         r'each.*month.*separately',
#         r'month.*separately',
#         r'monthly.*breakdown',
#         r'cost.*each.*month',
#         r'service.*each.*month',
#         r'monthly.*cost',
#         r'breakdown.*month'
#     ]
#
#     # Count/statistics patterns
#     count_patterns = [
#         r'how.*many.*account',
#         r'how.*many.*resource',
#         r'how.*many.*service',
#         r'count.*account',
#         r'count.*resource',
#         r'unique.*account',
#         r'total.*account'
#     ]
#
#     # Nonsensical/unclear patterns
#     unclear_patterns = [
#         r'^(what\??|huh\??|eh\??|\?\?+)$',
#         r'^(hmm+|um+|uh+)$',
#         r'^(\?+|\.+|\!+)$',
#         r'^(lee|ok|yes|no)$'
#     ]
#
#     # Financial/cost-related keywords
#     financial_keywords = [
#         'cost', 'price', 'spend', 'expense', 'bill', 'charge', 'money', 'dollar',
#         'invoice', 'month', '2025', 'total', 'how much', 'budget', 'unit_cost'
#     ]
#
#     # Check for greetings
#     for pattern in greeting_patterns:
#         if re.match(pattern, question_lower):
#             return 'greeting'
#
#     # Check for account queries
#     for pattern in account_patterns:
#         if re.search(pattern, question_lower):
#             return 'account_query'
#
#     # Check for resource queries
#     for pattern in resource_patterns:
#         if re.search(pattern, question_lower):
#             return 'resource_query'
#
#     # Check for count queries
#     for pattern in count_patterns:
#         if re.search(pattern, question_lower):
#             return 'count_query'
#
#     # Check for monthly breakdown
#     for pattern in monthly_breakdown_patterns:
#         if re.search(pattern, question_lower):
#             return 'monthly_breakdown'
#
#     # Check for service listing requests
#     for pattern in service_list_patterns:
#         if re.search(pattern, question_lower):
#             return 'service_list'
#
#     # Check for unclear/nonsensical queries
#     for pattern in unclear_patterns:
#         if re.match(pattern, question_lower):
#             return 'unclear'
#
#     # Check for financial keywords
#     has_financial_keywords = any(keyword in question_lower for keyword in financial_keywords)
#     has_time_reference = bool(re.search(
#         r'(2025|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}-\d{2})',
#         question_lower))
#
#     # Financial query if it has financial keywords or time references with context
#     if has_financial_keywords or (has_time_reference and len(question.split()) > 2):
#         return 'financial'
#
#     return 'unclear'
#
#
# def extract_account_id(question):
#     """Extract account ID from question"""
#     match = re.search(r'acct-([a-f0-9]+)', question.lower())
#     return f"acct-{match.group(1)}" if match else None
#
#
# def extract_resource_id(question):
#     """Extract resource ID from question"""
#     match = re.search(r'res-([a-f0-9]+)', question.lower())
#     return f"res-{match.group(1)}" if match else None
#
#
# def extract_service_filter(question):
#     """Extract specific service mentioned in the question"""
#     question_lower = question.lower()
#
#     # Direct service name matches
#     if 'ai' in question_lower:
#         return 'AI'
#     elif 'compute' in question_lower:
#         return 'Compute'
#     elif 'storage' in question_lower:
#         return 'Storage'
#     elif 'database' in question_lower or ' db ' in question_lower:
#         return 'DB'
#     elif 'network' in question_lower:
#         return 'Networking'
#
#     return None
#
#
# def extract_time_filter(question):
#     """Extract specific time period mentioned in the question"""
#     question_lower = question.lower()
#
#     # Look for year patterns
#     if 'year 2025' in question_lower or '2025 year' in question_lower:
#         return 'year_2025'
#
#     # Look for specific months
#     month_match = re.search(r'2025-(\d{2})', question)
#     if month_match:
#         return f"2025-{month_match.group(1)}"
#
#     # Look for month names
#     months = {
#         'january': '2025-01', 'february': '2025-02', 'march': '2025-03',
#         'april': '2025-04', 'may': '2025-05', 'june': '2025-06',
#         'july': '2025-07', 'august': '2025-08', 'september': '2025-09',
#         'october': '2025-10', 'november': '2025-11', 'december': '2025-12'
#     }
#
#     for month_name, month_code in months.items():
#         if month_name in question_lower or month_name[:3] in question_lower:
#             return month_code
#
#     return None
#
#
# def handle_account_query(question):
#     """Handle account-specific queries"""
#     account_id = extract_account_id(question)
#
#     if not account_id:
#         return {
#             'type': 'account_query',
#             'response': "I couldn't find a valid account ID in your question. Please use format like 'acct-1234' or ask about a specific account ID."
#         }
#
#     # Get all data for this account
#     billing_data = get_comprehensive_billing_data({'account_id': account_id})
#
#     if not billing_data:
#         return {
#             'type': 'account_query',
#             'response': f"No billing records found for account {account_id}. This account might not exist in your data or has no charges."
#         }
#
#     # Analyze the data
#     total_cost = sum(float(item['cost']) for item in billing_data)
#     unique_services = set(item['service'] for item in billing_data if item['service'])
#     unique_months = set(item['invoice_month'] for item in billing_data if item['invoice_month'])
#     total_transactions = len(billing_data)
#
#     # Service breakdown
#     service_costs = {}
#     for item in billing_data:
#         service = item['service']
#         cost = float(item['cost'])
#         if service in service_costs:
#             service_costs[service] += cost
#         else:
#             service_costs[service] = cost
#
#     # Generate response
#     response = f"Account {account_id} Details:\n\n"
#     response += f"💰 Total Spending: ${total_cost:,.2f}\n"
#     response += f"📊 Total Transactions: {total_transactions}\n"
#     response += f"🔧 Unique Services Used: {len(unique_services)}\n"
#     response += f"📅 Active Months: {len(unique_months)}\n\n"
#
#     if service_costs:
#         response += "Service Breakdown:\n"
#         sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
#         for service, cost in sorted_services:
#             percentage = (cost / total_cost) * 100
#             response += f"• {service}: ${cost:,.2f} ({percentage:.1f}%)\n"
#
#     if len(unique_months) > 1:
#         month_costs = {}
#         for item in billing_data:
#             month = item['invoice_month']
#             cost = float(item['cost'])
#             if month in month_costs:
#                 month_costs[month] += cost
#             else:
#                 month_costs[month] = cost
#
#         response += f"\nMonthly Breakdown:\n"
#         for month in sorted(month_costs.keys()):
#             response += f"• {get_month_name(month)}: ${month_costs[month]:,.2f}\n"
#
#     return {
#         'type': 'account_query',
#         'response': response,
#         'account_id': account_id,
#         'billing_data': billing_data
#     }
#
#
# def handle_resource_query(question):
#     """Handle resource-specific queries"""
#     resource_id = extract_resource_id(question)
#
#     if not resource_id:
#         return {
#             'type': 'resource_query',
#             'response': "I couldn't find a valid resource ID in your question. Please use format like 'res-abc123' or ask about a specific resource ID."
#         }
#
#     # Get all data for this resource
#     billing_data = get_comprehensive_billing_data({'resource_id': resource_id})
#
#     if not billing_data:
#         return {
#             'type': 'resource_query',
#             'response': f"No billing records found for resource {resource_id}. This resource might not exist in your data or has no charges."
#         }
#
#     # Analyze the data
#     resource_info = billing_data[0]  # Get first record for basic info
#     total_cost = sum(float(item['cost']) for item in billing_data)
#     service = resource_info['service']
#     region = resource_info['region']
#     resource_group = resource_info['resource_group']
#
#     response = f"Resource {resource_id} Details:\n\n"
#     response += f"🔧 Service: {service}\n"
#     response += f"📍 Region: {region}\n"
#     response += f"📁 Resource Group: {resource_group}\n"
#     response += f"💰 Total Cost: ${total_cost:,.2f}\n"
#     response += f"📊 Total Transactions: {len(billing_data)}\n\n"
#
#     # Monthly breakdown if multiple months
#     month_costs = {}
#     for item in billing_data:
#         month = item['invoice_month']
#         cost = float(item['cost'])
#         usage = float(item['usage_qty']) if item['usage_qty'] else 0
#         unit_cost = float(item['unit_cost']) if item['unit_cost'] else 0
#
#         if month not in month_costs:
#             month_costs[month] = {'cost': 0, 'usage': 0, 'unit_cost': unit_cost}
#         month_costs[month]['cost'] += cost
#         month_costs[month]['usage'] += usage
#
#     if len(month_costs) > 1:
#         response += "Monthly Usage & Costs:\n"
#         for month in sorted(month_costs.keys()):
#             data = month_costs[month]
#             response += f"• {get_month_name(month)}: ${data['cost']:,.2f}"
#             if data['usage'] > 0:
#                 response += f" (Usage: {data['usage']:,.2f} units)"
#             if data['unit_cost'] > 0:
#                 response += f" (Unit Cost: ${data['unit_cost']:,.4f})"
#             response += f"\n"
#
#     return {
#         'type': 'resource_query',
#         'response': response,
#         'resource_id': resource_id,
#         'billing_data': billing_data
#     }
#
#
# def handle_count_query(question):
#     """Handle count/statistics queries"""
#     question_lower = question.lower()
#
#     if 'account' in question_lower:
#         # Count unique accounts
#         try:
#             session = SessionLocal()
#             account_count = session.execute(
#                 select(func.count(distinct(models.Billing.account_id)))
#             ).scalar()
#             session.close()
#
#             return {
#                 'type': 'count_query',
#                 'response': f"Total unique accounts in your data: {account_count}"
#             }
#         except Exception as e:
#             return {
#                 'type': 'count_query',
#                 'response': f"Error counting accounts: {e}"
#             }
#
#     elif 'resource' in question_lower:
#         # Count unique resources
#         try:
#             session = SessionLocal()
#             resource_count = session.execute(
#                 select(func.count(distinct(models.Billing.resource_id)))
#             ).scalar()
#             session.close()
#
#             return {
#                 'type': 'count_query',
#                 'response': f"Total unique resources in your data: {resource_count}"
#             }
#         except Exception as e:
#             return {
#                 'type': 'count_query',
#                 'response': f"Error counting resources: {e}"
#             }
#
#     elif 'service' in question_lower:
#         # Count unique services
#         try:
#             session = SessionLocal()
#             service_count = session.execute(
#                 select(func.count(distinct(models.Billing.service)))
#             ).scalar()
#             session.close()
#
#             return {
#                 'type': 'count_query',
#                 'response': f"Total unique services in your data: {service_count}"
#             }
#         except Exception as e:
#             return {
#                 'type': 'count_query',
#                 'response': f"Error counting services: {e}"
#             }
#
#     return {
#         'type': 'count_query',
#         'response': "I can count accounts, resources, or services. Try: 'How many unique accounts are there?'"
#     }
#
#
# def handle_monthly_breakdown(question):
#     """Handle monthly breakdown queries"""
#     service_filter = extract_service_filter(question)
#
#     filters = {}
#     if service_filter:
#         filters['service'] = service_filter
#
#     billing_data = get_comprehensive_billing_data(filters)
#
#     if not billing_data:
#         service_text = f" for {service_filter}" if service_filter else ""
#         return {
#             'type': 'monthly_breakdown',
#             'response': f"No billing data found{service_text}. Make sure your data has been processed."
#         }
#
#     # Group by month
#     monthly_data = {}
#     total_cost = 0
#
#     for item in billing_data:
#         month = item['invoice_month']
#         cost = float(item['cost'])
#         usage = float(item['usage_qty']) if item['usage_qty'] else 0
#         unit_cost = float(item['unit_cost']) if item['unit_cost'] else 0
#
#         if month not in monthly_data:
#             monthly_data[month] = {
#                 'cost': 0,
#                 'usage': 0,
#                 'transactions': 0,
#                 'avg_unit_cost': 0,
#                 'unit_costs': []
#             }
#
#         monthly_data[month]['cost'] += cost
#         monthly_data[month]['usage'] += usage
#         monthly_data[month]['transactions'] += 1
#         if unit_cost > 0:
#             monthly_data[month]['unit_costs'].append(unit_cost)
#
#         total_cost += cost
#
#     # Calculate averages
#     for month_data in monthly_data.values():
#         if month_data['unit_costs']:
#             month_data['avg_unit_cost'] = sum(month_data['unit_costs']) / len(month_data['unit_costs'])
#
#     service_text = f" for {service_filter} service" if service_filter else ""
#     response = f"Monthly Breakdown{service_text}:\n\n"
#     response += f"Total Cost: ${total_cost:,.2f}\n\n"
#
#     for month in sorted(monthly_data.keys()):
#         data = monthly_data[month]
#         percentage = (data['cost'] / total_cost) * 100
#
#         response += f"📅 {get_month_name(month)}:\n"
#         response += f"   💰 Cost: ${data['cost']:,.2f} ({percentage:.1f}% of total)\n"
#         response += f"   📊 Transactions: {data['transactions']}\n"
#
#         if data['usage'] > 0:
#             response += f"   📈 Usage: {data['usage']:,.2f} units\n"
#
#         if data['avg_unit_cost'] > 0:
#             response += f"   💵 Avg Unit Cost: ${data['avg_unit_cost']:,.4f}\n"
#
#         response += f"\n"
#
#     return {
#         'type': 'monthly_breakdown',
#         'response': response,
#         'monthly_data': monthly_data,
#         'service_filter': service_filter
#     }
#
#
# def handle_service_list_query(question):
#     """Handle requests for listing services"""
#     question_lower = question.lower()
#
#     # Check if user wants just names (no costs)
#     wants_names_only = any(phrase in question_lower for phrase in [
#         'just names', 'only names', 'service names', 'name not', 'not cost', 'not percentage',
#         'without cost', 'without percentage', 'names only', 'list names'
#     ])
#
#     if wants_names_only:
#         try:
#             session = SessionLocal()
#             services = session.execute(
#                 select(distinct(models.Billing.service))
#                 .where(models.Billing.service.isnot(None))
#             ).scalars().all()
#             session.close()
#
#             if not services:
#                 return {
#                     'type': 'service_list',
#                     'response': "I couldn't find any services in your database."
#                 }
#
#             services = sorted([service for service in services if service and service.strip()])
#
#             response = f"Here are all the cloud services you've used:\n\n"
#             for i, service in enumerate(services, 1):
#                 response += f"{i}. {service}\n"
#
#             response += f"\nTotal: {len(services)} different services found in your records."
#
#             return {
#                 'type': 'service_list',
#                 'response': response,
#                 'services': services
#             }
#         except Exception as e:
#             return {
#                 'type': 'service_list',
#                 'response': f"Error retrieving services: {e}"
#             }
#
#     else:
#         # Get comprehensive service summary
#         billing_data = get_comprehensive_billing_data()
#
#         if not billing_data:
#             return {
#                 'type': 'service_list',
#                 'response': "I couldn't find any service data in your database."
#             }
#
#         service_summary = {}
#         total_cost = 0
#
#         for item in billing_data:
#             service = item['service']
#             cost = float(item['cost'])
#             month = item['invoice_month']
#
#             if service not in service_summary:
#                 service_summary[service] = {
#                     'total_cost': 0,
#                     'transaction_count': 0,
#                     'months': set()
#                 }
#
#             service_summary[service]['total_cost'] += cost
#             service_summary[service]['transaction_count'] += 1
#             service_summary[service]['months'].add(month)
#             total_cost += cost
#
#         # Sort services by total cost (descending)
#         sorted_services = sorted(service_summary.items(), key=lambda x: x[1]['total_cost'], reverse=True)
#
#         response = f"Here are all the cloud services you've used with their details:\n\n"
#
#         for i, (service, data) in enumerate(sorted_services, 1):
#             percentage = (data['total_cost'] / total_cost) * 100 if total_cost > 0 else 0
#             months_count = len(data['months'])
#
#             response += f"{i}. {service}\n"
#             response += f"   • Total spent: ${data['total_cost']:,.2f} ({percentage:.1f}% of all spending)\n"
#             response += f"   • Transactions: {data['transaction_count']}\n"
#             response += f"   • Active in {months_count} month{'s' if months_count != 1 else ''}\n\n"
#
#         response += f"Summary: {len(sorted_services)} different services, ${total_cost:,.2f} total spending"
#
#         return {
#             'type': 'service_list_detailed',
#             'response': response,
#             'service_data': service_summary,
#             'total_cost': total_cost
#         }
#
#
# def handle_financial_query(question):
#     """Handle financial queries with comprehensive data"""
#     service_filter = extract_service_filter(question)
#     time_filter = extract_time_filter(question)
#     account_id = extract_account_id(question)
#     resource_id = extract_resource_id(question)
#
#     # Build filters
#     filters = {}
#     if service_filter:
#         filters['service'] = service_filter
#     if time_filter:
#         if time_filter == 'year_2025':
#             filters['year'] = '2025'
#         else:
#             filters['month'] = time_filter
#     if account_id:
#         filters['account_id'] = account_id
#     if resource_id:
#         filters['resource_id'] = resource_id
#
#     # Get comprehensive data
#     billing_data = get_comprehensive_billing_data(filters)
#
#     if not billing_data:
#         return {
#             'type': 'financial',
#             'response': "I couldn't find any billing data matching your criteria. Please check your filters and try again."
#         }
#
#     # Generate comprehensive response
#     total_cost = sum(float(item['cost']) for item in billing_data)
#     transaction_count = len(billing_data)
#
#     response_parts = []
#
#     # Main summary
#     filter_description = []
#     if service_filter:
#         filter_description.append(f"{service_filter} service")
#     if time_filter:
#         if time_filter == 'year_2025':
#             filter_description.append("in 2025")
#         else:
#             filter_description.append(f"in {get_month_name(time_filter)}")
#     if account_id:
#         filter_description.append(f"for account {account_id}")
#     if resource_id:
#         filter_description.append(f"for resource {resource_id}")
#
#     filter_text = " ".join(filter_description) if filter_description else ""
#
#     response_parts.append(
#         f"Found {transaction_count} transactions{' ' + filter_text if filter_text else ''} totaling ${total_cost:,.2f}.")
#
#     # Service breakdown (if not filtered by service)
#     if not service_filter:
#         services = {}
#         for item in billing_data:
#             service = item['service']
#             cost = float(item['cost'])
#             if service in services:
#                 services[service] += cost
#             else:
#                 services[service] = cost
#
#         if len(services) > 1:
#             response_parts.append("Service breakdown:")
#             sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
#             for service, cost in sorted_services[:5]:
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {service}: ${cost:,.2f} ({percentage:.1f}%)")
#
#     # Monthly breakdown (if not filtered by specific month)
#     if not time_filter or time_filter == 'year_2025':
#         months = {}
#         for item in billing_data:
#             month = item['invoice_month']
#             cost = float(item['cost'])
#             if month in months:
#                 months[month] += cost
#             else:
#                 months[month] = cost
#
#         if len(months) > 1:
#             response_parts.append("Monthly breakdown:")
#             for month in sorted(months.keys()):
#                 cost = months[month]
#                 percentage = (cost / total_cost) * 100
#                 response_parts.append(f"• {get_month_name(month)}: ${cost:,.2f} ({percentage:.1f}%)")
#
#     return {
#         'type': 'financial',
#         'response': " ".join(response_parts),
#         'billing_data': billing_data,
#         'filters': filters
#     }
#
#
# def handle_greeting():
#     """Handle greeting queries"""
#     greetings = [
#         "Hello! I'm FinBot, your cloud cost assistant. 😊",
#         "Hi there! I'm here to help you understand your cloud spending.",
#         "Namaste! I can help you analyze your cloud costs and expenses.",
#         "Hello! Ready to dive into your cloud financial data?"
#     ]
#
#     import random
#     greeting = random.choice(greetings)
#
#     return {
#         'type': 'greeting',
#         'response': f"{greeting} Ask me questions like:\n• 'What did we spend on AI services in 2025?'\n• 'Show me account acct-5609 details'\n• 'List all services'"
#     }
#
#
# def handle_unclear_query():
#     """Handle unclear or nonsensical queries"""
#     return {
#         'type': 'unclear',
#         'response': "I'm not sure what you're asking about. 🤔\n\nI can help you with:\n• Cloud costs: 'What did we spend on AI in July 2025?'\n• Account details: 'Show me account acct-5609 details'\n• Resource info: 'What service does res-abc123 belong to?'\n• Service lists: 'List all services'\n• Counts: 'How many unique accounts are there?'\n\nType 'help' for more examples!"
#     }
#
#
# def get_month_name(month_code):
#     """Convert month code to readable name"""
#     if not month_code:
#         return "Unknown month"
#
#     month_names = {
#         '2025-01': 'January 2025', '2025-02': 'February 2025', '2025-03': 'March 2025',
#         '2025-04': 'April 2025', '2025-05': 'May 2025', '2025-06': 'June 2025',
#         '2025-07': 'July 2025', '2025-08': 'August 2025', '2025-09': 'September 2025',
#         '2025-10': 'October 2025', '2025-11': 'November 2025', '2025-12': 'December 2025'
#     }
#     return month_names.get(month_code, month_code)
#
#
# def process_query(question: str, k: int = 5):
#     """Process a user question with comprehensive classification"""
#
#     # First classify the query
#     query_type = classify_query(question)
#
#     print(f"🔍 Query classified as: {query_type}")
#
#     # Route to appropriate handler
#     if query_type == 'greeting':
#         return handle_greeting()
#
#     elif query_type == 'unclear':
#         return handle_unclear_query()
#
#     elif query_type == 'account_query':
#         return handle_account_query(question)
#
#     elif query_type == 'resource_query':
#         return handle_resource_query(question)
#
#     elif query_type == 'count_query':
#         return handle_count_query(question)
#
#     elif query_type == 'monthly_breakdown':
#         return handle_monthly_breakdown(question)
#
#     elif query_type == 'service_list':
#         return handle_service_list_query(question)
#
#     elif query_type == 'financial':
#         return handle_financial_query(question)
#
#     else:
#         return handle_unclear_query()
#
#
# def display_response(response_data):
#     """Display the appropriate response based on type"""
#     if not response_data:
#         return
#
#     response_type = response_data.get('type')
#
#     # Handle simple responses
#     if response_type in ['greeting', 'unclear', 'service_list', 'count_query']:
#         print(f"\n💬 {response_data['response']}")
#         return
#
#     # Handle complex responses with formatting
#     print("\n" + "=" * 70)
#     print("💼 FinBot - Enhanced Cloud Cost Assistant")
#     print("=" * 70)
#
#     print(f"\n🎯 Query Type: {response_type.replace('_', ' ').title()}")
#     print(f"\n📋 Analysis:")
#     print("-" * 40)
#     print(response_data['response'])
#
#     # Show additional details if available
#     if response_data.get('billing_data'):
#         print(f"\n📈 Found {len(response_data['billing_data'])} detailed records in database")
#
#
# def show_help():
#     """Display enhanced help information"""
#     help_text = """
# 🚀 FinBot - Enhanced Cloud Cost Assistant
# ========================================
#
# I can understand many types of questions about your cloud spending!
#
# 💰 FINANCIAL QUESTIONS:
# • "What did we spend on AI services in 2025?"
# • "Show me storage costs for July 2025"
# • "Get total cost of Compute service in year 2025"
#
# 👤 ACCOUNT QUERIES:
# • "Show me account acct-5609 details"
# • "What is total cost of account acct-1234"
# • "How many services used by account acct-5609"
#
# 🔧 RESOURCE QUERIES:
# • "What service does resource res-abc123 belong to"
# • "Show me resource res-def456 costs"
#
# 📊 MONTHLY BREAKDOWNS:
# • "AI service cost in each month separately"
# • "Show monthly breakdown for Storage service"
#
# 📋 SERVICE & COUNT QUERIES:
# • "List all services" / "List service names only"
# • "How many unique accounts are there"
# • "How many resources do we have"
#
# 💡 GREETINGS:
# • "Hi", "Hello" - I'll greet you back without searching data
#
# 🔧 COMMANDS:
# • 'help' - This help menu
# • 'embed' - Process CSV data
# • 'status' - System status
# • 'quit' - Exit
# """
#     print(help_text)
#
#
# def check_system_status():
#     """Enhanced system status check"""
#     try:
#         from app.configs import FAISS_INDEX_FILE
#         index_path = Path(FAISS_INDEX_FILE)
#
#         print("\n🔍 System Status Check:")
#         print("-" * 30)
#
#         # Check FAISS index
#         if index_path.exists():
#             file_size = index_path.stat().st_size
#             print(f"✅ FAISS Index: Ready ({file_size:,} bytes)")
#         else:
#             print("❌ FAISS Index: Not found")
#
#         # Check database connectivity
#         try:
#             session = SessionLocal()
#
#             # Count records
#             total_records = session.execute(
#                 select(func.count(models.Billing.id))
#             ).scalar()
#
#             unique_services = session.execute(
#                 select(func.count(distinct(models.Billing.service)))
#             ).scalar()
#
#             unique_accounts = session.execute(
#                 select(func.count(distinct(models.Billing.account_id)))
#             ).scalar()
#
#             unique_resources = session.execute(
#                 select(func.count(distinct(models.Billing.resource_id)))
#             ).scalar()
#
#             unique_months = session.execute(
#                 select(func.count(distinct(models.Billing.invoice_month)))
#             ).scalar()
#
#             session.close()
#
#             print(f"✅ Database: Connected")
#             print(f"   📊 Total records: {total_records:,}")
#             print(f"   🔧 Services: {unique_services}")
#             print(f"   👤 Accounts: {unique_accounts}")
#             print(f"   📦 Resources: {unique_resources}")
#             print(f"   📅 Months: {unique_months}")
#             print("   System ready for all query types!")
#
#             return True
#
#         except Exception as e:
#             print(f"❌ Database: Connection failed - {e}")
#             return False
#
#     except Exception as e:
#         print(f"❌ System check failed: {e}")
#         return False
#
#
# def main():
#     """Enhanced main interface"""
#     print("🚀 Starting FinBot - Enhanced Cloud Cost Assistant")
#     print("=" * 60)
#
#     # Check system status
#     system_ready = check_system_status()
#
#     if not system_ready:
#         print("\n⚠️  System not ready! Please run 'embed' command first.")
#
#     show_help()
#
#     print("\n🗣️  Ready to help with comprehensive cloud cost analysis!")
#     print("💡 Try: 'Hi', 'Account acct-5609 details', 'AI costs each month', 'List services'")
#
#     # Main interaction loop
#     while True:
#         try:
#             user_input = input("\n💬 Ask FinBot> ").strip()
#
#             if not user_input:
#                 print("🤔 Please ask me something!")
#                 continue
#
#             # Handle system commands
#             if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
#                 print("👋 Thanks for using FinBot! Have a great day!")
#                 break
#
#             elif user_input.lower() in ['help', '?', 'h']:
#                 show_help()
#                 continue
#
#             elif user_input.lower() == 'embed':
#                 print("🔄 Processing your data...")
#                 try:
#                     stats = embed_all_and_store()
#                     print(f"\n🎉 Success! Processed {stats['added_vectors']} new records")
#                     system_ready = True
#                 except Exception as e:
#                     print(f"❌ Processing failed: {e}")
#                 continue
#
#             elif user_input.lower() in ['status', 'check']:
#                 check_system_status()
#                 continue
#
#             # Process the query
#             response_data = process_query(user_input)
#             display_response(response_data)
#
#         except KeyboardInterrupt:
#             print("\n\n👋 Thanks for using FinBot! Goodbye!")
#             break
#         except EOFError:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Something went wrong: {e}")
#             logger.exception("Unexpected error in main loop")
#
#
# if __name__ == "__main__":
#     main()


# #!/usr/bin/env python3
# """
# Enhanced Terminal RAG System – now with Resource-metadata support
# """
#
# import json, logging, re
# from pathlib import Path
# from sqlalchemy import select, distinct, func
#
# # ── project imports ───────────────────────────────────────────────────
# from app.services.embedder import query_knn, embed_all_and_store
# from backend.prompts       import build_simple_prompt, get_enhanced_examples
# from app.db.base           import SessionLocal
# from app.db                import models
#
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)
#
# # ╔══════════════════════════════════════════════════════════════════╗
# # ║                       DATABASE HELPERS                           ║
# # ╚══════════════════════════════════════════════════════════════════╝
# def get_comprehensive_billing_data(filters: dict | None = None):
#     try:
#         s = SessionLocal()
#         q = select(models.Billing)
#         if filters:
#             if filters.get("service"):
#                 q = q.where(models.Billing.service.ilike(f"%{filters['service']}%"))
#             if filters.get("account_id"):
#                 q = q.where(models.Billing.account_id == filters["account_id"])
#             if filters.get("resource_id"):
#                 q = q.where(models.Billing.resource_id == filters["resource_id"])
#             if filters.get("resource_ids"):
#                 q = q.where(models.Billing.resource_id.in_(filters["resource_ids"]))
#             if filters.get("month"):
#                 q = q.where(models.Billing.invoice_month == filters["month"])
#             if filters.get("year"):
#                 q = q.where(models.Billing.invoice_month.like(f"{filters['year']}%"))
#         rows = s.execute(q).scalars().all()
#         s.close()
#         return [
#             dict(
#                 invoice_month=r.invoice_month,
#                 account_id=r.account_id,
#                 subscription=r.subscription,
#                 service=r.service,
#                 resource_group=r.resource_group,
#                 resource_id=r.resource_id,
#                 region=r.region,
#                 usage_qty=r.usage_qty,
#                 unit_cost=r.unit_cost,
#                 cost=r.cost,
#             )
#             for r in rows
#         ]
#     except Exception as e:
#         logger.error("billing fetch error: %s", e)
#         return []
#
# # ── NEW  resource-metadata helpers ───────────────────────────────────
# def get_resources_by_owner(owner: str):
#     with SessionLocal() as s:
#         return (
#             s.query(models.Resource)
#             .filter(models.Resource.owner.ilike(f"%{owner}%"))
#             .all()
#         )
#
# def get_resources_by_env(env: str):
#     with SessionLocal() as s:
#         return (
#             s.query(models.Resource)
#             .filter(models.Resource.env.ilike(f"%{env}%"))
#             .all()
#         )
#
# def get_complete_resource_data(res_id: str):
#     with SessionLocal() as s:
#         meta = (
#             s.query(models.Resource)
#             .filter(models.Resource.resource_id == res_id)
#             .one_or_none()
#         )
#     billing = get_comprehensive_billing_data({"resource_id": res_id})
#     return {"meta": meta, "billing": billing}
#
# # ╔══════════════════════════════════════════════════════════════════╗
# # ║                          CLASSIFIER                              ║
# # ╚══════════════════════════════════════════════════════════════════╝
# def classify_query(q: str) -> str:
#     ql = q.lower().strip()
#     if re.match(r"^(hi+|hello|hey|ram ram|namaste|hii+)$", ql):
#         return "greeting"
#
#     # NEW patterns ----------------------------------------------------
#     if re.search(r"owner\s+[a-z]+\s+[a-z]+", ql):
#         return "owner_query"
#     if re.search(r"\benv\b.*\b(dev|test|prod|staging)\b", ql):
#         return "env_query"
#     # -----------------------------------------------------------------
#
#     if re.search(r"account.*acct-[a-f0-9]+|acct-[a-f0-9]+", ql):
#         return "account_query"
#     if re.search(r"resource.*res-[a-f0-9]+|res-[a-f0-9]+", ql):
#         return "resource_query"
#     if re.search(r"list.*services?|show.*services?|all.*services?", ql):
#         return "service_list"
#     if re.search(r"each.*month|monthly.*breakdown|cost.*each.*month", ql):
#         return "monthly_breakdown"
#     if re.search(r"how.*many.*(account|resource|service)|unique.*account", ql):
#         return "count_query"
#     if any(k in ql for k in ["cost", "spend", "price", "dollar", "unit_cost"]):
#         return "financial"
#     return "unclear"
#
# # ── id / service / time extractors (unchanged) ───────────────────────
# def extract_account_id(q): m=re.search(r"acct-([a-f0-9]+)",q,re.I);return f"acct-{m.group(1)}" if m else None
# def extract_resource_id(q):m=re.search(r"res-([a-f0-9]+)",q,re.I);return f"res-{m.group(1)}" if m else None
# def extract_service_filter(q):
#     ql=q.lower()
#     if "ai" in ql: return "AI"
#     if "compute" in ql: return "Compute"
#     if "storage" in ql: return "Storage"
#     if "database" in ql or " db " in ql: return "DB"
#     if "network" in ql: return "Networking"
#     return None
# def extract_time_filter(q):
#     ql=q.lower()
#     if "year 2025" in ql: return "year_2025"
#     m=re.search(r"2025-(\d{2})",q);   # YYYY-MM
#     if m: return f"2025-{m.group(1)}"
#     months = {m: f"2025-{i:02d}" for i,m in enumerate(
#         ["january","february","march","april","may","june",
#          "july","august","september","october","november","december"],1)}
#     for n,c in months.items():
#         if n in ql or n[:3] in ql: return c
#     return None
#
# # ╔════════════ HANDLERS – only new / modified ones shown ═════════════╗
# def handle_greeting():   return {"type":"greeting","response":"Hi! Ask about costs or owners, e.g. 'owner Brian Torres details'."}
# def handle_unclear():    return {"type":"unclear","response":"Sorry, not sure what you need. Try 'env test resources'."}
#
# # NEW  owner query ----------------------------------------------------
# def handle_owner_query(q):
#     m=re.search(r"owner\s+([A-Za-z]+\s+[A-Za-z]+)",q,re.I)
#     if not m: return {"type":"owner_query","response":"Please include an owner name."}
#     owner=m.group(1)
#     rows=get_resources_by_owner(owner)
#     if not rows: return {"type":"owner_query","response":f"No resources for {owner}."}
#     res_ids=[r.resource_id for r in rows]
#     bill=get_comprehensive_billing_data({"resource_ids":res_ids})
#     total=sum(float(b["cost"]) for b in bill)
#     svc={}
#     for b in bill: svc[b["service"]]=svc.get(b["service"],0)+float(b["cost"])
#     resp=f"Owner {owner}: {len(rows)} resources, spend ${total:,.2f}\n"
#     if svc:
#         resp+="Service spending:\n"
#         for s,c in sorted(svc.items(),key=lambda x:x[1],reverse=True):
#             resp+=f"• {s}: ${c:,.2f}\n"
#     resp+="\nResource IDs (env):\n"
#     resp+="\n".join(f"• {r.resource_id} ({r.env or 'n/a'})" for r in rows[:10])
#     return {"type":"owner_query","response":resp}
#
# # NEW  env query ------------------------------------------------------
# def handle_env_query(q):
#     env=re.search(r"\b(dev|test|prod|staging)\b",q,re.I).group(1)
#     rows=get_resources_by_env(env)
#     if not rows: return {"type":"env_query","response":f"No resources in env '{env}'."}
#     owners={}
#     for r in rows: owners.setdefault(r.owner or "Unassigned",[]).append(r.resource_id)
#     resp=f"Environment '{env}' – {len(rows)} resources, {len(owners)} owners\n"
#     for o,ids in owners.items(): resp+=f"• {o}: {len(ids)} resources\n"
#     return {"type":"env_query","response":resp}
#
# # MODIFIED resource query – adds metadata -----------------------------
# def handle_resource_query(q):
#     rid=extract_resource_id(q)
#     if not rid: return {"type":"resource_query","response":"Provide a resource id (res-xxxx)."}
#     data=get_complete_resource_data(rid)
#     meta,bill=data["meta"],data["billing"]
#     if meta is None and not bill:
#         return {"type":"resource_query","response":f"No data for {rid}."}
#     resp=f"Resource {rid}\n\n"
#     if meta:
#         resp+="📋 Metadata\n"
#         resp+=f"• owner: {meta.owner or 'n/a'}\n"
#         resp+=f"• env  : {meta.env or 'n/a'}\n"
#         tag=(meta.tags_json or "")[:120]
#         resp+=f"• tags : {tag + ('…' if len(tag)==120 else '')}\n\n"
#     if bill:
#         total=sum(float(b['cost']) for b in bill)
#         first=bill[0]
#         resp+="💰 Billing\n"
#         resp+=f"• service: {first['service']}\n"
#         resp+=f"• region : {first['region']}\n"
#         resp+=f"• total  : ${total:,.2f} ({len(bill)} records)\n"
#     return {"type":"resource_query","response":resp}
#
# # keep your existing account / count / monthly / service / financial handlers here …
# # ───────────────────────────────────────────────────────────────
# #  BUSINESS-HANDLERS  (restored exactly as before)
# # ───────────────────────────────────────────────────────────────
# def handle_count_query(question):
#     ql = question.lower()
#     try:
#         s = SessionLocal()
#         if "account" in ql:
#             n = s.execute(select(func.count(distinct(models.Billing.account_id)))).scalar()
#             return {"type": "count_query", "response": f"Total unique accounts: {n}"}
#         if "resource" in ql:
#             n = s.execute(select(func.count(distinct(models.Billing.resource_id)))).scalar()
#             return {"type": "count_query", "response": f"Total unique resources: {n}"}
#         if "service" in ql:
#             n = s.execute(select(func.count(distinct(models.Billing.service)))).scalar()
#             return {"type": "count_query", "response": f"Total unique services:  {n}"}
#     finally:
#         s.close()
#     return {"type": "count_query", "response": "Specify account / resource / service to count."}
#
#
# def handle_monthly_breakdown(question):
#     svc = extract_service_filter(question)
#     billing = get_comprehensive_billing_data({"service": svc} if svc else None)
#     if not billing:
#         txt = f" for {svc}" if svc else ""
#         return {"type": "monthly_breakdown",
#                 "response": f"No billing data{txt}."}
#
#     months, total = {}, 0
#     for b in billing:
#         m, c = b["invoice_month"], float(b["cost"])
#         months[m] = months.get(m, 0) + c
#         total += c
#
#     resp = f"Monthly breakdown{' for ' + svc if svc else ''} – total ${total:,.2f}\n"
#     for m in sorted(months):
#         pct = months[m] / total * 100
#         resp += f"• {m}: ${months[m]:,.2f} ({pct:.1f}%)\n"
#     return {"type": "monthly_breakdown", "response": resp, "billing_data": billing}
#
#
# def handle_service_list_query(question):
#     want_names = any(p in question.lower() for p in
#                      ["only names", "just names", "names only", "list names", "without cost"])
#     billing = get_comprehensive_billing_data()
#     if not billing:
#         return {"type": "service_list", "response": "No billing data."}
#
#     if want_names:
#         svcs = sorted({b["service"] for b in billing if b["service"]})
#         resp = "Services used:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(svcs))
#         return {"type": "service_list", "response": resp, "services": svcs}
#
#     by, total = {}, 0
#     for b in billing:
#         by[b["service"]] = by.get(b["service"], 0) + float(b["cost"])
#         total += float(b["cost"])
#
#     resp = "Services with totals:\n"
#     for i, (s, c) in enumerate(sorted(by.items(), key=lambda x: x[1], reverse=True), 1):
#         resp += f"{i}. {s}: ${c:,.2f} ({(c / total) * 100:.1f}%)\n"
#     return {"type": "service_list_detailed", "response": resp, "service_data": by}
#
# # ───────────────────────────────────────────────────────────────
# #  ACCOUNT + FINANCIAL  (restored handlers)
# # ───────────────────────────────────────────────────────────────
# def handle_account_query(question):
#     account_id = extract_account_id(question)
#     if not account_id:
#         return {"type":"account_query",
#                 "response":"Please include an account id like acct-1234."}
#
#     billing = get_comprehensive_billing_data({"account_id": account_id})
#     if not billing:
#         return {"type":"account_query",
#                 "response":f"No billing rows for account {account_id}."}
#
#     total  = sum(float(b["cost"]) for b in billing)
#     svcs   = {}
#     months = {}
#     for b in billing:
#         svcs[b["service"]]  = svcs.get(b["service"],0)+float(b["cost"])
#         months[b["invoice_month"]] = months.get(b["invoice_month"],0)+float(b["cost"])
#
#     resp  = f"Account {account_id} spent ${total:,.2f} across {len(billing)} records.\n"
#     resp += "Service breakdown:\n"
#     for s,c in sorted(svcs.items(), key=lambda x:x[1], reverse=True):
#         resp += f"• {s}: ${c:,.2f}\n"
#     if len(months) > 1:
#         resp += "\nMonthly totals:\n"
#         for m,c in sorted(months.items()):
#             resp += f"• {m}: ${c:,.2f}\n"
#     return {"type":"account_query","response":resp,"billing_data":billing}
#
#
# def handle_financial_query(question):
#     svc  = extract_service_filter(question)
#     time = extract_time_filter(question)
#     acc  = extract_account_id(question)
#     res  = extract_resource_id(question)
#
#     filters={}
#     if svc: filters["service"]=svc
#     if time:
#         if time=="year_2025": filters["year"]="2025"
#         else: filters["month"]=time
#     if acc: filters["account_id"]=acc
#     if res: filters["resource_id"]=res
#
#     billing = get_comprehensive_billing_data(filters)
#     if not billing:
#         return {"type":"financial",
#                 "response":"No billing rows match those filters."}
#
#     total = sum(float(b["cost"]) for b in billing)
#     resp  = f"{len(billing)} transactions found — total ${total:,.2f}.\n"
#
#     if not svc:
#         bysvc={}
#         for b in billing:
#             bysvc[b["service"]] = bysvc.get(b["service"],0)+float(b["cost"])
#         if len(bysvc)>1:
#             resp+="Service breakdown:\n"
#             for s,c in sorted(bysvc.items(), key=lambda x:x[1], reverse=True)[:5]:
#                 pct=(c/total)*100
#                 resp+=f"• {s}: ${c:,.2f} ({pct:.1f}%)\n"
#
#     return {"type":"financial","response":resp,"billing_data":billing}
# # ───────────────────────────────────────────────────────────────
#
# # ───────────────────────────────────────────────────────────────
#
#
#
# # ────────────────────────────────────────────────────────────────────
#
#
# # ╔════════════ ROUTER ════════════╗
# def process_query(q):
#     t=classify_query(q)
#     if t=="greeting": return handle_greeting()
#     if t=="unclear":  return handle_unclear()
#     if t=="owner_query": return handle_owner_query(q)
#     if t=="env_query":   return handle_env_query(q)
#     if t=="resource_query": return handle_resource_query(q)
#     # keep existing routes
#     if t=="account_query":   return handle_account_query(q)
#     if t=="count_query":     return handle_count_query(q)
#     if t=="monthly_breakdown": return handle_monthly_breakdown(q)
#     if t=="service_list":    return handle_service_list_query(q)
#     if t=="financial":       return handle_financial_query(q)
#     return handle_unclear()
#
# # ╔════════════ DISPLAY ═══════════╗
# def display_response(r):
#     if not r: return
#     simple={'greeting','unclear','service_list','count_query','owner_query','env_query'}
#     if r['type'] in simple:
#         print("\n💬",r['response']);return
#     print("\n"+("="*60))
#     print(r['response'])
#
# # ╔════════════ MAIN LOOP ═════════╗
# if __name__=="__main__":
#     print("🚀 FinBot ready")
#     try:
#         while True:
#             q=input("\n💬 > ").strip()
#             if q.lower() in {"exit","quit"}: break
#             display_response(process_query(q))
#     except KeyboardInterrupt:
#         pass
#


# !/usr/bin/env python3
"""
Enhanced Terminal RAG System – now with Resource-metadata support
"""

import json, logging, re
from pathlib import Path
from sqlalchemy import select, distinct, func

# ── project imports ───────────────────────────────────────────────────
from app.services.embedder import query_knn, embed_all_and_store
from backend.prompts import build_simple_prompt, get_enhanced_examples
from app.db.base import SessionLocal
from app.db import models

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════════════════╗
# ║                       DATABASE HELPERS                           ║
# ╚══════════════════════════════════════════════════════════════════╝
def get_comprehensive_billing_data(filters: dict | None = None):
    try:
        s = SessionLocal()
        q = select(models.Billing)
        if filters:
            if filters.get("service"):
                q = q.where(models.Billing.service.ilike(f"%{filters['service']}%"))
            if filters.get("account_id"):
                q = q.where(models.Billing.account_id == filters["account_id"])
            if filters.get("resource_id"):
                q = q.where(models.Billing.resource_id == filters["resource_id"])
            if filters.get("resource_ids"):
                q = q.where(models.Billing.resource_id.in_(filters["resource_ids"]))
            if filters.get("month"):
                q = q.where(models.Billing.invoice_month == filters["month"])
            if filters.get("year"):
                q = q.where(models.Billing.invoice_month.like(f"{filters['year']}%"))
        rows = s.execute(q).scalars().all()
        s.close()
        return [
            dict(
                invoice_month=r.invoice_month,
                account_id=r.account_id,
                subscription=r.subscription,
                service=r.service,
                resource_group=r.resource_group,
                resource_id=r.resource_id,
                region=r.region,
                usage_qty=r.usage_qty,
                unit_cost=r.unit_cost,
                cost=r.cost,
            )
            for r in rows
        ]
    except Exception as e:
        logger.error("billing fetch error: %s", e)
        return []


# ── NEW  resource-metadata helpers ───────────────────────────────────
def get_resources_by_owner(owner: str):
    with SessionLocal() as s:
        return (
            s.query(models.Resource)
            .filter(models.Resource.owner.ilike(f"%{owner}%"))
            .all()
        )


def get_resources_by_env(env: str):
    with SessionLocal() as s:
        return (
            s.query(models.Resource)
            .filter(models.Resource.env.ilike(f"%{env}%"))
            .all()
        )


def get_complete_resource_data(res_id: str):
    with SessionLocal() as s:
        meta = (
            s.query(models.Resource)
            .filter(models.Resource.resource_id == res_id)
            .one_or_none()
        )
    billing = get_comprehensive_billing_data({"resource_id": res_id})
    return {"meta": meta, "billing": billing}


# ╔══════════════════════════════════════════════════════════════════╗
# ║                          CLASSIFIER                              ║
# ╚══════════════════════════════════════════════════════════════════╝
def classify_query(q: str) -> str:
    ql = q.lower().strip()
    if re.match(r"^(hi+|hello|hey|ram ram|namaste|hii+)$", ql):
        return "greeting"

    # NEW: Schema/table structure queries
    if re.search(r"(list|show|describe).*(columns?|fields?|structure).*table", ql):
        return "schema_query"
    if re.search(r"columns? (of|in|from).*(table|resources)", ql):
        return "schema_query"

    # NEW: General listing queries
    if re.search(r"list\s+(down\s+)?all.*(resource_id|resources?)", ql):
        return "resource_list_query"
    if re.search(r"list\s+(down\s+)?all.*(including|with).*(owner|env|tags)", ql):
        return "detailed_resource_list_query"

    # NEW patterns ----------------------------------------------------
    if re.search(r"owner\s+[a-z]+\s+[a-z]+", ql):
        return "owner_query"
    if re.search(r"\benv\b.*\b(dev|test|prod|staging)\b", ql):
        return "env_query"
    # -----------------------------------------------------------------

    if re.search(r"account.*acct-[a-f0-9]+|acct-[a-f0-9]+", ql):
        return "account_query"
    if re.search(r"resource.*res-[a-f0-9]+|res-[a-f0-9]+", ql):
        return "resource_query"
    if re.search(r"list.*services?|show.*services?|all.*services?", ql):
        return "service_list"
    if re.search(r"each.*month|monthly.*breakdown|cost.*each.*month", ql):
        return "monthly_breakdown"
    if re.search(r"how.*many.*(account|resource|service)|unique.*account", ql):
        return "count_query"
    if any(k in ql for k in ["cost", "spend", "price", "dollar", "unit_cost"]):
        return "financial"
    return "unclear"


# ── id / service / time extractors (unchanged) ───────────────────────
def extract_account_id(q): m = re.search(r"acct-([a-f0-9]+)", q, re.I);return f"acct-{m.group(1)}" if m else None


def extract_resource_id(q): m = re.search(r"res-([a-f0-9]+)", q, re.I);return f"res-{m.group(1)}" if m else None


def extract_service_filter(q):
    ql = q.lower()
    if "ai" in ql: return "AI"
    if "compute" in ql: return "Compute"
    if "storage" in ql: return "Storage"
    if "database" in ql or " db " in ql: return "DB"
    if "network" in ql: return "Networking"
    return None


def extract_time_filter(q):
    ql = q.lower()
    if "year 2025" in ql: return "year_2025"
    m = re.search(r"2025-(\d{2})", q);  # YYYY-MM
    if m: return f"2025-{m.group(1)}"
    months = {m: f"2025-{i:02d}" for i, m in enumerate(
        ["january", "february", "march", "april", "may", "june",
         "july", "august", "september", "october", "november", "december"], 1)}
    for n, c in months.items():
        if n in ql or n[:3] in ql: return c
    return None


# ╔════════════ HANDLERS – only new / modified ones shown ═════════════╗
def handle_greeting():   return {"type": "greeting",
                                 "response": "Hi! Ask about costs or owners, e.g. 'owner Brian Torres details'."}


def handle_unclear():    return {"type": "unclear",
                                 "response": "Sorry, not sure what you need. Try 'env test resources'."}


# NEW: Schema query handler
def handle_schema_query(q):
    """Handle queries about table structure/columns"""
    if "resources" in q.lower():
        try:
            s = SessionLocal()
            # Get sample resource to show column structure
            sample = s.query(models.Resource).first()
            s.close()

            if sample:
                columns = []
                for column in sample.__table__.columns:
                    columns.append(f"• {column.name} ({column.type})")

                resp = "Resources table columns:\n" + "\n".join(columns)
                return {"type": "schema_query", "response": resp}
            else:
                return {"type": "schema_query", "response": "Resources table exists but no data to show structure."}
        except Exception as e:
            logger.error("Schema query error: %s", e)
            return {"type": "schema_query", "response": "Error accessing table schema."}

    return {"type": "schema_query", "response": "Specify which table schema you want to see."}


# NEW: Resource list handler
def handle_resource_list_query(q):
    """Handle general resource listing queries"""
    try:
        s = SessionLocal()

        # Check if environment filter is specified
        env_match = re.search(r"\bfor\s+env\s+(\w+)", q, re.I)
        if env_match:
            env = env_match.group(1)
            resources = s.query(models.Resource).filter(
                models.Resource.env.ilike(f"%{env}%")
            ).all()
            resp = f"Resource IDs for env '{env}':\n"
        else:
            resources = s.query(models.Resource).limit(50).all()  # Limit to avoid overflow
            resp = "All Resource IDs (first 50):\n"

        s.close()

        if not resources:
            return {"type": "resource_list_query", "response": "No resources found."}

        for r in resources:
            resp += f"• {r.resource_id}\n"

        return {"type": "resource_list_query", "response": resp}

    except Exception as e:
        logger.error("Resource list query error: %s", e)
        return {"type": "resource_list_query", "response": "Error fetching resource list."}


# NEW: Detailed resource list handler
def handle_detailed_resource_list_query(q):
    """Handle detailed resource listing with owner, env, tags"""
    try:
        s = SessionLocal()

        # Check for environment filter
        env_match = re.search(r"\bfor\s+env\s+(\w+)", q, re.I)
        if env_match:
            env = env_match.group(1)
            resources = s.query(models.Resource).filter(
                models.Resource.env.ilike(f"%{env}%")
            ).limit(50).all()
            resp = f"Detailed resource list for env '{env}':\n\n"
        else:
            resources = s.query(models.Resource).limit(20).all()  # Smaller limit for detailed view
            resp = "Detailed resource list (first 20):\n\n"

        s.close()

        if not resources:
            return {"type": "detailed_resource_list_query", "response": "No resources found."}

        for r in resources:
            resp += f"🔹 {r.resource_id}\n"
            resp += f"   Owner: {r.owner or 'n/a'}\n"
            resp += f"   Env: {r.env or 'n/a'}\n"
            tags = (r.tags_json or "")[:100]  # Truncate tags
            resp += f"   Tags: {tags + ('...' if len(tags) == 100 else '')}\n\n"

        return {"type": "detailed_resource_list_query", "response": resp}

    except Exception as e:
        logger.error("Detailed resource list query error: %s", e)
        return {"type": "detailed_resource_list_query", "response": "Error fetching detailed resource list."}


# NEW  owner query ----------------------------------------------------
def handle_owner_query(q):
    m = re.search(r"owner\s+([A-Za-z]+\s+[A-Za-z]+)", q, re.I)
    if not m: return {"type": "owner_query", "response": "Please include an owner name."}
    owner = m.group(1)
    rows = get_resources_by_owner(owner)
    if not rows: return {"type": "owner_query", "response": f"No resources for {owner}."}
    res_ids = [r.resource_id for r in rows]
    bill = get_comprehensive_billing_data({"resource_ids": res_ids})
    total = sum(float(b["cost"]) for b in bill)
    svc = {}
    for b in bill: svc[b["service"]] = svc.get(b["service"], 0) + float(b["cost"])
    resp = f"Owner {owner}: {len(rows)} resources, spend ${total:,.2f}\n"
    if svc:
        resp += "Service spending:\n"
        for s, c in sorted(svc.items(), key=lambda x: x[1], reverse=True):
            resp += f"• {s}: ${c:,.2f}\n"
    resp += "\nResource IDs (env):\n"
    resp += "\n".join(f"• {r.resource_id} ({r.env or 'n/a'})" for r in rows[:10])
    return {"type": "owner_query", "response": resp}


# NEW  env query ------------------------------------------------------
def handle_env_query(q):
    env = re.search(r"\b(dev|test|prod|staging)\b", q, re.I).group(1)
    rows = get_resources_by_env(env)
    if not rows: return {"type": "env_query", "response": f"No resources in env '{env}'."}
    owners = {}
    for r in rows: owners.setdefault(r.owner or "Unassigned", []).append(r.resource_id)
    resp = f"Environment '{env}' – {len(rows)} resources, {len(owners)} owners\n"
    for o, ids in owners.items(): resp += f"• {o}: {len(ids)} resources\n"
    return {"type": "env_query", "response": resp}


# MODIFIED resource query – adds metadata -----------------------------
def handle_resource_query(q):
    rid = extract_resource_id(q)
    if not rid: return {"type": "resource_query", "response": "Provide a resource id (res-xxxx)."}
    data = get_complete_resource_data(rid)
    meta, bill = data["meta"], data["billing"]
    if meta is None and not bill:
        return {"type": "resource_query", "response": f"No data for {rid}."}
    resp = f"Resource {rid}\n\n"
    if meta:
        resp += "📋 Metadata\n"
        resp += f"• owner: {meta.owner or 'n/a'}\n"
        resp += f"• env  : {meta.env or 'n/a'}\n"
        tag = (meta.tags_json or "")[:120]
        resp += f"• tags : {tag + ('…' if len(tag) == 120 else '')}\n\n"
    if bill:
        total = sum(float(b['cost']) for b in bill)
        first = bill[0]
        resp += "💰 Billing\n"
        resp += f"• service: {first['service']}\n"
        resp += f"• region : {first['region']}\n"
        resp += f"• total  : ${total:,.2f} ({len(bill)} records)\n"
    return {"type": "resource_query", "response": resp}


# ───────────────────────────────────────────────────────────────
#  BUSINESS-HANDLERS  (restored exactly as before)
# ───────────────────────────────────────────────────────────────
def handle_count_query(question):
    ql = question.lower()
    try:
        s = SessionLocal()
        if "account" in ql:
            n = s.execute(select(func.count(distinct(models.Billing.account_id)))).scalar()
            return {"type": "count_query", "response": f"Total unique accounts: {n}"}
        if "resource" in ql:
            n = s.execute(select(func.count(distinct(models.Billing.resource_id)))).scalar()
            return {"type": "count_query", "response": f"Total unique resources: {n}"}
        if "service" in ql:
            n = s.execute(select(func.count(distinct(models.Billing.service)))).scalar()
            return {"type": "count_query", "response": f"Total unique services:  {n}"}
    finally:
        s.close()
    return {"type": "count_query", "response": "Specify account / resource / service to count."}


def handle_monthly_breakdown(question):
    svc = extract_service_filter(question)
    billing = get_comprehensive_billing_data({"service": svc} if svc else None)
    if not billing:
        txt = f" for {svc}" if svc else ""
        return {"type": "monthly_breakdown",
                "response": f"No billing data{txt}."}

    months, total = {}, 0
    for b in billing:
        m, c = b["invoice_month"], float(b["cost"])
        months[m] = months.get(m, 0) + c
        total += c

    resp = f"Monthly breakdown{' for ' + svc if svc else ''} – total ${total:,.2f}\n"
    for m in sorted(months):
        pct = months[m] / total * 100
        resp += f"• {m}: ${months[m]:,.2f} ({pct:.1f}%)\n"
    return {"type": "monthly_breakdown", "response": resp, "billing_data": billing}


def handle_service_list_query(question):
    want_names = any(p in question.lower() for p in
                     ["only names", "just names", "names only", "list names", "without cost"])
    billing = get_comprehensive_billing_data()
    if not billing:
        return {"type": "service_list", "response": "No billing data."}

    if want_names:
        svcs = sorted({b["service"] for b in billing if b["service"]})
        resp = "Services used:\n" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(svcs))
        return {"type": "service_list", "response": resp, "services": svcs}

    by, total = {}, 0
    for b in billing:
        by[b["service"]] = by.get(b["service"], 0) + float(b["cost"])
        total += float(b["cost"])

    resp = "Services with totals:\n"
    for i, (s, c) in enumerate(sorted(by.items(), key=lambda x: x[1], reverse=True), 1):
        resp += f"{i}. {s}: ${c:,.2f} ({(c / total) * 100:.1f}%)\n"
    return {"type": "service_list_detailed", "response": resp, "service_data": by}


# ───────────────────────────────────────────────────────────────
#  ACCOUNT + FINANCIAL  (restored handlers)
# ───────────────────────────────────────────────────────────────
def handle_account_query(question):
    account_id = extract_account_id(question)
    if not account_id:
        return {"type": "account_query",
                "response": "Please include an account id like acct-1234."}

    billing = get_comprehensive_billing_data({"account_id": account_id})
    if not billing:
        return {"type": "account_query",
                "response": f"No billing rows for account {account_id}."}

    total = sum(float(b["cost"]) for b in billing)
    svcs = {}
    months = {}
    for b in billing:
        svcs[b["service"]] = svcs.get(b["service"], 0) + float(b["cost"])
        months[b["invoice_month"]] = months.get(b["invoice_month"], 0) + float(b["cost"])

    resp = f"Account {account_id} spent ${total:,.2f} across {len(billing)} records.\n"
    resp += "Service breakdown:\n"
    for s, c in sorted(svcs.items(), key=lambda x: x[1], reverse=True):
        resp += f"• {s}: ${c:,.2f}\n"
    if len(months) > 1:
        resp += "\nMonthly totals:\n"
        for m, c in sorted(months.items()):
            resp += f"• {m}: ${c:,.2f}\n"
    return {"type": "account_query", "response": resp, "billing_data": billing}


def handle_financial_query(question):
    svc = extract_service_filter(question)
    time = extract_time_filter(question)
    acc = extract_account_id(question)
    res = extract_resource_id(question)

    filters = {}
    if svc: filters["service"] = svc
    if time:
        if time == "year_2025":
            filters["year"] = "2025"
        else:
            filters["month"] = time
    if acc: filters["account_id"] = acc
    if res: filters["resource_id"] = res

    billing = get_comprehensive_billing_data(filters)
    if not billing:
        return {"type": "financial",
                "response": "No billing rows match those filters."}

    total = sum(float(b["cost"]) for b in billing)
    resp = f"{len(billing)} transactions found — total ${total:,.2f}.\n"

    if not svc:
        bysvc = {}
        for b in billing:
            bysvc[b["service"]] = bysvc.get(b["service"], 0) + float(b["cost"])
        if len(bysvc) > 1:
            resp += "Service breakdown:\n"
            for s, c in sorted(bysvc.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = (c / total) * 100
                resp += f"• {s}: ${c:,.2f} ({pct:.1f}%)\n"

    return {"type": "financial", "response": resp, "billing_data": billing}


# ───────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────


# ╔════════════ ROUTER ════════════╗
def process_query(q):
    t = classify_query(q)
    if t == "greeting": return handle_greeting()
    if t == "unclear": return handle_unclear()

    # NEW handlers
    if t == "schema_query": return handle_schema_query(q)
    if t == "resource_list_query": return handle_resource_list_query(q)
    if t == "detailed_resource_list_query": return handle_detailed_resource_list_query(q)

    # Existing handlers
    if t == "owner_query": return handle_owner_query(q)
    if t == "env_query": return handle_env_query(q)
    if t == "resource_query": return handle_resource_query(q)
    if t == "account_query": return handle_account_query(q)
    if t == "count_query": return handle_count_query(q)
    if t == "monthly_breakdown": return handle_monthly_breakdown(q)
    if t == "service_list": return handle_service_list_query(q)
    if t == "financial": return handle_financial_query(q)

    return handle_unclear()


# ╔════════════ DISPLAY ═══════════╗
def display_response(r):
    if not r: return
    simple = {'greeting', 'unclear', 'service_list', 'count_query', 'owner_query', 'env_query', 'schema_query',
              'resource_list_query', 'detailed_resource_list_query'}
    if r['type'] in simple:
        print("\n💬", r['response'])
        return
    print("\n" + ("=" * 60))
    print(r['response'])


# ╔════════════ MAIN LOOP ═════════╗
if __name__ == "__main__":
    print("🚀 FinBot ready")
    try:
        while True:
            q = input("\n💬 > ").strip()
            if q.lower() in {"exit", "quit"}: break
            display_response(process_query(q))
    except KeyboardInterrupt:
        pass
