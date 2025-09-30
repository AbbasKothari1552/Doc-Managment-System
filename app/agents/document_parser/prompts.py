CATEGORY_PREDICTION_PROMPT = """
        You are a document classifier. Given the document content, return only the most appropriate category name from the following list:

        {', '.join(CATEGORY_LIST)}

        Return ONLY the category name. Do not include any explanation, formatting, or additional words.

        Example Output:
        Technical

        Document content:

        {doc_text}
        """