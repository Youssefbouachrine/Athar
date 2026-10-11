import unittest
import mwparserfromhell

class TestWikitextParser(unittest.TestCase):
    def test_link_extraction(self):
        sample_wikitext = """
        == أعضاء المجموعة ==
        * [[User:RedaMorocco|رضا]]
        * [[User:FatimaWiki|فاطمة]]
        * [[User:TestUser/Sandbox|مسودة]]
        """
        code = mwparserfromhell.parse(sample_wikitext)
        users = []
        for link in code.filter_wikilinks():
            target = str(link.title).strip()
            if target.startswith("User:"):
                user = target.replace("User:", "").split("/")[0].strip()
                users.append(user)

        self.assertIn("RedaMorocco", users)
        self.assertIn("FatimaWiki", users)
        self.assertIn("TestUser", users)
        self.assertEqual(len(users), 3)

if __name__ == "__main__":
    unittest.main()
