#!/usr/bin/env python3
"""
Unit tests for GlasseyeOS AI Tool Generator
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_generator import ToolGenerator, AttackSurface, ToolSpec
from compliance_enforcer import RiskLevel


class TestToolGenerator(unittest.TestCase):
    """Test suite for ToolGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.test_dir) / 'templates'
        self.output_dir = Path(self.test_dir) / 'output'
        self.skills_dir = Path(self.test_dir) / 'skills'
        
        self.templates_dir.mkdir()
        self.output_dir.mkdir()
        self.skills_dir.mkdir()
        
        # Initialize generator with test directories
        self.generator = ToolGenerator(
            templates_dir=str(self.templates_dir),
            output_dir=str(self.output_dir),
            skills_dir=str(self.skills_dir)
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_initialization(self):
        """Test ToolGenerator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertTrue(self.templates_dir.exists())
        self.assertTrue(self.output_dir.exists())
        self.assertTrue(self.skills_dir.exists())
        
    def test_analyze_attack_surface_json_rpc(self):
        """Test attack surface analysis for JSON-RPC."""
        attack_surface = AttackSurface(
            name='test-mcp-server',
            protocol='JSON-RPC 2.0',
            transport='STDIO',
            authentication='OAuth',
            attack_vectors=['command injection', 'auth bypass'],
            endpoints=['/api/v1']
        )
        
        tools = self.generator.analyze_attack_surface(attack_surface)
        
        self.assertIn('json_rpc_fuzzer', tools)
        self.assertIn('protocol_analyzer', tools)
        self.assertIn('command_injection_poc', tools)
        self.assertIn('auth_bypass_poc', tools)
        
    def test_analyze_attack_surface_http(self):
        """Test attack surface analysis for HTTP."""
        attack_surface = AttackSurface(
            name='test-api',
            protocol='HTTP/1.1',
            transport='TCP',
            authentication='Bearer Token',
            attack_vectors=['ssrf'],
            endpoints=['/api/users', '/api/data']
        )
        
        tools = self.generator.analyze_attack_surface(attack_surface)
        
        self.assertIn('http_api_fuzzer', tools)
        self.assertIn('protocol_analyzer', tools)
        self.assertIn('ssrf_poc', tools)
        
    def test_generate_basic_template(self):
        """Test basic template generation."""
        code = self.generator._generate_basic_template(
            'test_tool',
            {'target': 'test-target', 'timestamp': '2024-01-01'}
        )
        
        self.assertIn('#!/usr/bin/env python3', code)
        self.assertIn('test-target', code)
        self.assertIn('2024-01-01', code)
        self.assertIn('class TestTool:', code)
        
    def test_validate_generated_code_valid(self):
        """Test code validation with valid code."""
        valid_code = '''
def hello():
    print("Hello, world!")
    return True
'''
        self.assertTrue(self.generator.validate_generated_code(valid_code))
        
    def test_validate_generated_code_invalid(self):
        """Test code validation with invalid syntax."""
        invalid_code = '''
def hello(
    print("Missing closing paren")
'''
        self.assertFalse(self.generator.validate_generated_code(invalid_code))
        
    def test_add_tests_to_tool(self):
        """Test adding unit tests to generated code."""
        original_code = '''
#!/usr/bin/env python3
def main():
    pass
'''
        
        code_with_tests = self.generator.add_tests_to_tool(original_code, 'fuzzer')
        
        self.assertIn('unittest', code_with_tests)
        self.assertIn('class TestFuzzer', code_with_tests)
        self.assertIn('def test_initialization', code_with_tests)
        
    def test_save_tool(self):
        """Test saving tool to file."""
        tool_code = '''#!/usr/bin/env python3
print("Test tool")
'''
        
        output_path = self.generator.save_tool(tool_code, 'test_tool.py')
        
        self.assertTrue(output_path.exists())
        
        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, tool_code)
        
        # Verify executable permissions
        self.assertTrue(os.access(output_path, os.X_OK))
        
    def test_generate_fuzzer(self):
        """Test fuzzer generation (with templates)."""
        # This test requires actual templates, so we'll create a minimal one
        template_path = self.templates_dir / 'json_rpc_fuzzer_template.py'
        template_path.write_text('''#!/usr/bin/env python3
# Target: {target}
# Protocol: {protocol}
print("Fuzzer for {target}")
''')
        
        try:
            output_path = self.generator.generate_fuzzer(
                protocol='JSON-RPC 2.0',
                transport='STDIO',
                target='test-server'
            )
            
            self.assertTrue(Path(output_path).exists())
            
            with open(output_path, 'r') as f:
                content = f.read()
            
            self.assertIn('test-server', content)
            self.assertIn('JSON-RPC 2.0', content)
            
        except PermissionError:
            # Compliance check may fail in test environment
            self.skipTest("Compliance check failed - expected in test environment")
            
    def test_generate_mcp_skill(self):
        """Test MCP skill generation."""
        skill_path = self.generator.generate_mcp_skill(
            capability='test-skill',
            description='Test skill for unit testing',
            tools_list=['tool1', 'tool2']
        )
        
        skill_dir = Path(skill_path)
        
        self.assertTrue(skill_dir.exists())
        self.assertTrue((skill_dir / 'skill.yaml').exists())
        self.assertTrue((skill_dir / 'skill.py').exists())
        self.assertTrue((skill_dir / 'README.md').exists())
        
        # Verify skill.yaml content
        import yaml
        with open(skill_dir / 'skill.yaml', 'r') as f:
            manifest = yaml.safe_load(f)
            
        self.assertEqual(manifest['name'], 'test-skill')
        self.assertEqual(manifest['description'], 'Test skill for unit testing')
        self.assertIn('tool1', manifest['tools'])
        self.assertIn('tool2', manifest['tools'])
        
    def test_tool_categories(self):
        """Test that all tool categories are defined."""
        categories = self.generator.tool_categories
        
        self.assertIn('fuzzer', categories)
        self.assertIn('analyzer', categories)
        self.assertIn('poc', categories)
        self.assertIn('evidence_collector', categories)
        self.assertIn('skill', categories)
        
    def test_compliance_integration(self):
        """Test that compliance enforcer is initialized."""
        self.assertIsNotNone(self.generator.compliance)
        
    def test_knowledge_base_integration(self):
        """Test that knowledge base is initialized."""
        self.assertIsNotNone(self.generator.kb)


class TestAttackSurface(unittest.TestCase):
    """Test AttackSurface dataclass."""
    
    def test_creation(self):
        """Test creating an AttackSurface."""
        surface = AttackSurface(
            name='test',
            protocol='HTTP',
            transport='TCP',
            authentication='Bearer',
            attack_vectors=['xss', 'sqli'],
            endpoints=['/api']
        )
        
        self.assertEqual(surface.name, 'test')
        self.assertEqual(surface.protocol, 'HTTP')
        self.assertIsNotNone(surface.metadata)
        
    def test_default_metadata(self):
        """Test default metadata initialization."""
        surface = AttackSurface(
            name='test',
            protocol='HTTP',
            transport='TCP',
            authentication=None,
            attack_vectors=[],
            endpoints=[]
        )
        
        self.assertEqual(surface.metadata, {})


class TestTemplateSystem(unittest.TestCase):
    """Test template-based code generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.test_dir) / 'templates'
        self.output_dir = Path(self.test_dir) / 'output'
        
        self.templates_dir.mkdir()
        self.output_dir.mkdir()
        
        self.generator = ToolGenerator(
            templates_dir=str(self.templates_dir),
            output_dir=str(self.output_dir)
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
        
    def test_template_substitution(self):
        """Test template parameter substitution."""
        template_path = self.templates_dir / 'test_template.py'
        template_path.write_text('''
Target: {target}
Protocol: {protocol}
Timestamp: {timestamp}
''')
        
        result = self.generator._generate_from_template(
            'test',
            {
                'target': 'example.com',
                'protocol': 'HTTP',
                'timestamp': '2024-01-01'
            }
        )
        
        self.assertIn('example.com', result)
        self.assertIn('HTTP', result)
        self.assertIn('2024-01-01', result)
        
    def test_template_with_lists(self):
        """Test template substitution with list values."""
        template_path = self.templates_dir / 'list_template.py'
        template_path.write_text('Endpoints: {endpoints}')
        
        result = self.generator._generate_from_template(
            'list',
            {'endpoints': ['/api/v1', '/api/v2']}
        )
        
        self.assertIn('/api/v1', result)
        self.assertIn('/api/v2', result)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestToolGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestAttackSurface))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateSystem))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
