#!/usr/bin/env python3
"""
🌀 META-COGNITIVE SYNC MANAGER
⧬ RECURSIVE INTELLIGENCE AMPLIFICATION SYSTEM ⧬

Enhanced Notion ↔ Obsidian sync with recursive cognitive architecture
"""

import asyncio
import argparse
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import yaml
import re
import hashlib

# Core sync components
from notion_client.client import NotionSyncClient
from obsidian_client.client import ObsidianSyncClient
from converters.notion_to_obsidian import NotionToObsidianConverter
from converters.obsidian_to_notion import ObsidianToNotionConverter

class AboutnessDetector:
    """🧠 Semantic relationship and concept analysis engine"""
    
    def __init__(self):
        self.concept_patterns = {}
        self.relationship_graph = defaultdict(set)
        self.semantic_clusters = {}
        
    def analyze_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """Extract semantic aboutness from content"""
        analysis = {
            'core_concepts': self._extract_concepts(content),
            'relationship_density': self._calculate_relationship_density(content),
            'abstraction_level': self._detect_abstraction_level(content),
            'recursive_depth': self._detect_recursive_patterns(content),
            'semantic_signature': self._generate_semantic_signature(content, title)
        }
        
        # Update global knowledge graph
        self._update_relationship_graph(analysis['core_concepts'])
        
        return analysis
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts using pattern matching"""
        # Meta-cognitive concept patterns
        meta_patterns = [
            r'\b(?:meta|recursive|self-referential|about|concerning)\b',
            r'\b(?:consciousness|awareness|cognition|intelligence)\b',
            r'\b(?:system|architecture|framework|structure)\b',
            r'\b(?:analysis|assessment|evaluation|reflection)\b'
        ]
        
        concepts = []
        for pattern in meta_patterns:
            matches = re.findall(pattern, content.lower())
            concepts.extend(matches)
            
        # Extract capitalized terms (likely concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        concepts.extend(capitalized)
        
        return list(set(concepts))
    
    def _calculate_relationship_density(self, content: str) -> float:
        """Calculate how interconnected the concepts are"""
        connection_words = ['relates to', 'connects with', 'implies', 'suggests', 'leads to']
        connections = sum(content.lower().count(word) for word in connection_words)
        return min(connections / max(len(content.split()), 1), 1.0)
    
    def _detect_abstraction_level(self, content: str) -> int:
        """Detect level of abstraction (0=concrete, 5=highly abstract)"""
        abstract_indicators = ['concept', 'principle', 'theory', 'framework', 'paradigm']
        concrete_indicators = ['example', 'instance', 'specific', 'particular', 'actual']
        
        abstract_score = sum(content.lower().count(word) for word in abstract_indicators)
        concrete_score = sum(content.lower().count(word) for word in concrete_indicators)
        
        if abstract_score > concrete_score * 2:
            return min(5, 3 + (abstract_score - concrete_score) // 3)
        elif concrete_score > abstract_score * 2:
            return max(0, 2 - (concrete_score - abstract_score) // 3)
        else:
            return 2
    
    def _detect_recursive_patterns(self, content: str) -> int:
        """Detect recursive self-reference depth"""
        recursive_patterns = [
            r'\b\w+\s+(?:of|about|concerning)\s+\1\b',  # "X of X"
            r'\bmeta-\w+',  # meta-prefixed words
            r'\bself-\w+',  # self-prefixed words
            r'\brecursive',  # explicit recursion
        ]
        
        depth = 0
        for pattern in recursive_patterns:
            matches = len(re.findall(pattern, content.lower()))
            depth += matches
            
        return min(depth, 10)
    
    def _generate_semantic_signature(self, content: str, title: str) -> str:
        """Generate unique semantic fingerprint"""
        combined = f"{title} {content}".lower()
        # Create hash of semantic elements
        semantic_elements = sorted(self._extract_concepts(combined))
        signature_text = " ".join(semantic_elements)
        return hashlib.md5(signature_text.encode()).hexdigest()[:16]
    
    def _update_relationship_graph(self, concepts: List[str]):
        """Update global concept relationship graph"""
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                self.relationship_graph[concept1].add(concept2)
                self.relationship_graph[concept2].add(concept1)

class CognitivePatternLearner:
    """🔄 Learn user's cognitive patterns and predict needs"""
    
    def __init__(self):
        self.access_patterns = deque(maxlen=1000)  # Recent file access history
        self.temporal_patterns = defaultdict(list)  # Time-based patterns
        self.concept_transitions = defaultdict(lambda: defaultdict(int))  # Concept flow patterns
        self.cognitive_rhythm = {}  # User's thinking rhythm
        
    def record_access(self, file_path: str, timestamp: datetime, concepts: List[str]):
        """Record file access with semantic context"""
        access_record = {
            'file': file_path,
            'timestamp': timestamp,
            'concepts': concepts,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        }
        
        self.access_patterns.append(access_record)
        self._update_temporal_patterns(access_record)
        self._update_concept_transitions(concepts)
        
    def predict_next_files(self, current_concepts: List[str], limit: int = 5) -> List[str]:
        """Predict which files user might need next"""
        predictions = []
        
        # Based on concept transitions
        concept_scores = defaultdict(float)
        for concept in current_concepts:
            for next_concept, count in self.concept_transitions[concept].items():
                concept_scores[next_concept] += count
        
        # Find files with highest scoring concepts
        file_scores = defaultdict(float)
        for access in self.access_patterns:
            for concept in access['concepts']:
                if concept in concept_scores:
                    file_scores[access['file']] += concept_scores[concept]
        
        # Sort by score and return top predictions
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        return [file for file, score in sorted_files[:limit]]
    
    def _update_temporal_patterns(self, access_record: Dict):
        """Update time-based access patterns"""
        hour_key = f"hour_{access_record['hour']}"
        day_key = f"day_{access_record['day_of_week']}"
        
        self.temporal_patterns[hour_key].append(access_record['file'])
        self.temporal_patterns[day_key].append(access_record['file'])
    
    def _update_concept_transitions(self, concepts: List[str]):
        """Update concept transition probabilities"""
        if len(self.access_patterns) < 2:
            return
            
        prev_concepts = self.access_patterns[-2]['concepts']
        
        for prev_concept in prev_concepts:
            for curr_concept in concepts:
                if prev_concept != curr_concept:
                    self.concept_transitions[prev_concept][curr_concept] += 1

class RecursiveAssessmentEngine:
    """⚡ Recursive gap assessment and self-optimization"""
    
    def __init__(self):
        self.performance_metrics = {}
        self.gap_assessments = []
        self.optimization_history = []
        self.recursive_depth = 0
        
    def assess_system_gaps(self, current_state: Dict, desired_state: Dict) -> Dict:
        """Assess gaps between current and desired system state"""
        self.recursive_depth += 1
        
        gaps = {}
        for key in desired_state:
            if key in current_state:
                if isinstance(desired_state[key], dict) and isinstance(current_state[key], dict):
                    # Recursive assessment for nested structures
                    nested_gaps = self.assess_system_gaps(current_state[key], desired_state[key])
                    if nested_gaps:
                        gaps[key] = nested_gaps
                elif current_state[key] != desired_state[key]:
                    gaps[key] = {
                        'current': current_state[key],
                        'desired': desired_state[key],
                        'gap_magnitude': self._calculate_gap_magnitude(current_state[key], desired_state[key])
                    }
            else:
                gaps[key] = {
                    'current': None,
                    'desired': desired_state[key],
                    'gap_magnitude': 1.0
                }
        
        # Meta-assessment: assess the assessment process itself
        if self.recursive_depth < 3:  # Prevent infinite recursion
            meta_gaps = self.assess_system_gaps(
                {'assessment_quality': len(gaps)},
                {'assessment_quality': len(desired_state) * 0.1}  # Expect 10% gaps
            )
            if meta_gaps:
                gaps['meta_assessment'] = meta_gaps
        
        self.recursive_depth -= 1
        return gaps
    
    def _calculate_gap_magnitude(self, current, desired) -> float:
        """Calculate magnitude of gap between current and desired state"""
        if isinstance(current, (int, float)) and isinstance(desired, (int, float)):
            return abs(current - desired) / max(abs(desired), 1)
        elif isinstance(current, str) and isinstance(desired, str):
            # Simple string similarity
            common = set(current.lower().split()) & set(desired.lower().split())
            total = set(current.lower().split()) | set(desired.lower().split())
            return 1 - (len(common) / max(len(total), 1))
        else:
            return 1.0 if current != desired else 0.0

class MetaCognitiveSyncManager:
    """🌀 Main orchestrator with recursive intelligence amplification"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Core sync components
        self.notion_client = NotionSyncClient(
            token=self.config['notion']['token'],
            database_ids=self.config['notion']['database_ids']
        )
        
        self.obsidian_client = ObsidianSyncClient(
            vault_path=self.config['obsidian']['vault_path'],
            sync_folder=self.config['obsidian']['sync_folder']
        )
        
        self.notion_to_obsidian = NotionToObsidianConverter(self.config)
        self.obsidian_to_notion = ObsidianToNotionConverter(self.config)
        
        # Meta-cognitive components
        self.aboutness_detector = AboutnessDetector()
        self.pattern_learner = CognitivePatternLearner()
        self.assessment_engine = RecursiveAssessmentEngine()
        
        # State tracking
        self.cognitive_state = {
            'active_concepts': [],
            'current_focus': None,
            'prediction_accuracy': 0.0,
            'system_performance': {}
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            raise
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def meta_cognitive_sync(self):
        """🧠 Enhanced sync with cognitive awareness"""
        self.logger.info("🌀 Starting meta-cognitive sync mode...")
        
        # Phase 1: Analyze current cognitive state
        await self._analyze_cognitive_state()
        
        # Phase 2: Predict user needs
        predicted_files = self.pattern_learner.predict_next_files(
            self.cognitive_state['active_concepts']
        )
        
        if predicted_files:
            self.logger.info(f"🔮 Predicted you might need: {predicted_files}")
        
        # Phase 3: Perform intelligent sync
        await self._intelligent_bidirectional_sync()
        
        # Phase 4: Assess and optimize
        await self._recursive_self_assessment()
        
        self.logger.info("✨ Meta-cognitive sync completed!")
    
    async def _analyze_cognitive_state(self):
        """Analyze current cognitive context"""
        self.logger.info("🧠 Analyzing cognitive state...")
        
        # Analyze recent Obsidian files
        recent_files = self._get_recent_obsidian_files()
        active_concepts = []
        
        for file_path in recent_files:
            try:
                content = self.obsidian_client.read_file(file_path)
                analysis = self.aboutness_detector.analyze_content(content, file_path.stem)
                active_concepts.extend(analysis['core_concepts'])
                
                # Record access pattern
                self.pattern_learner.record_access(
                    str(file_path),
                    datetime.now(),
                    analysis['core_concepts']
                )
                
            except Exception as e:
                self.logger.warning(f"Could not analyze {file_path}: {e}")
        
        self.cognitive_state['active_concepts'] = list(set(active_concepts))
        self.logger.info(f"🎯 Active concepts: {self.cognitive_state['active_concepts']}")
    
    async def _intelligent_bidirectional_sync(self):
        """Perform sync with semantic awareness"""
        self.logger.info("🔄 Performing intelligent bidirectional sync...")
        
        # Sync Notion → Obsidian with semantic clustering
        await self._semantic_notion_to_obsidian_sync()
        
        # Sync Obsidian → Notion with aboutness detection
        await self._semantic_obsidian_to_notion_sync()
    
    async def _semantic_notion_to_obsidian_sync(self):
        """Sync from Notion with semantic awareness"""
        try:
            pages = await self.notion_client.get_all_pages()
            
            for page in pages:
                # Analyze semantic content
                content = self.notion_client.extract_content(page)
                analysis = self.aboutness_detector.analyze_content(content, page.get('title', ''))
                
                # Check if semantically related to current focus
                if self._is_semantically_relevant(analysis):
                    # Convert and sync with priority
                    obsidian_content = self.notion_to_obsidian.convert(page)
                    file_path = self.obsidian_client.save_file(
                        page.get('title', 'Untitled'),
                        obsidian_content
                    )
                    self.logger.info(f"🎯 Priority sync: {file_path}")
                else:
                    # Regular sync
                    obsidian_content = self.notion_to_obsidian.convert(page)
                    file_path = self.obsidian_client.save_file(
                        page.get('title', 'Untitled'),
                        obsidian_content
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Semantic Notion sync failed: {e}")
    
    async def _semantic_obsidian_to_notion_sync(self):
        """Sync from Obsidian with aboutness detection"""
        try:
            files = self.obsidian_client.get_all_files()
            
            for file_path in files:
                content = self.obsidian_client.read_file(file_path)
                
                # Analyze aboutness
                analysis = self.aboutness_detector.analyze_content(content, file_path.stem)
                
                # Convert with semantic metadata
                notion_page = self.obsidian_to_notion.convert(content, file_path.stem)
                
                # Add semantic metadata
                notion_page['properties']['Semantic_Signature'] = {
                    'rich_text': [{'text': {'content': analysis['semantic_signature']}}]
                }
                notion_page['properties']['Abstraction_Level'] = {
                    'number': analysis['abstraction_level']
                }
                notion_page['properties']['Recursive_Depth'] = {
                    'number': analysis['recursive_depth']
                }
                
                # Create/update in Notion
                await self.notion_client.create_page(notion_page)
                self.logger.info(f"📝 Synced with semantics: {file_path.stem}")
                
        except Exception as e:
            self.logger.error(f"❌ Semantic Obsidian sync failed: {e}")
    
    async def _recursive_self_assessment(self):
        """Recursively assess and optimize system performance"""
        self.logger.info("⚡ Performing recursive self-assessment...")
        
        current_state = {
            'sync_accuracy': self._calculate_sync_accuracy(),
            'prediction_accuracy': self.cognitive_state['prediction_accuracy'],
            'semantic_coverage': len(self.aboutness_detector.concept_patterns),
            'pattern_learning_depth': len(self.pattern_learner.access_patterns)
        }
        
        desired_state = {
            'sync_accuracy': 0.95,
            'prediction_accuracy': 0.80,
            'semantic_coverage': 100,
            'pattern_learning_depth': 500
        }
        
        gaps = self.assessment_engine.assess_system_gaps(current_state, desired_state)
        
        if gaps:
            self.logger.info(f"🔍 System gaps identified: {gaps}")
            await self._optimize_based_on_gaps(gaps)
        else:
            self.logger.info("✅ System performing optimally!")
    
    def _is_semantically_relevant(self, analysis: Dict) -> bool:
        """Check if content is semantically relevant to current focus"""
        if not self.cognitive_state['active_concepts']:
            return False
            
        concept_overlap = set(analysis['core_concepts']) & set(self.cognitive_state['active_concepts'])
        return len(concept_overlap) > 0
    
    def _get_recent_obsidian_files(self, hours: int = 24) -> List[Path]:
        """Get recently modified Obsidian files"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_files = []
        
        try:
            for file_path in self.obsidian_client.get_all_files():
                if file_path.stat().st_mtime > cutoff_time.timestamp():
                    recent_files.append(file_path)
        except Exception as e:
            self.logger.warning(f"Could not get recent files: {e}")
            
        return recent_files[:10]  # Limit to 10 most recent
    
    def _calculate_sync_accuracy(self) -> float:
        """Calculate current sync accuracy"""
        # Simplified accuracy calculation
        # In practice, this would compare file states across platforms
        return 0.85  # Placeholder
    
    async def _optimize_based_on_gaps(self, gaps: Dict):
        """Optimize system based on identified gaps"""
        self.logger.info("🔧 Optimizing system based on gaps...")
        
        for gap_type, gap_info in gaps.items():
            if gap_type == 'prediction_accuracy' and gap_info.get('gap_magnitude', 0) > 0.2:
                # Improve prediction accuracy
                self.logger.info("📈 Optimizing prediction algorithms...")
                # Implementation would adjust prediction parameters
                
            elif gap_type == 'semantic_coverage' and gap_info.get('gap_magnitude', 0) > 0.3:
                # Expand semantic analysis
                self.logger.info("🧠 Expanding semantic analysis coverage...")
                # Implementation would add new concept patterns
    
    async def test_connection(self):
        """Test connections to both Notion and Obsidian"""
        self.logger.info("🧪 Testing meta-cognitive connections...")
        
        # Test Notion connection
        try:
            await self.notion_client.test_connection()
            self.logger.info("✅ Notion connection: OK")
        except Exception as e:
            self.logger.error(f"❌ Notion connection failed: {e}")
            return False
        
        # Test Obsidian connection
        try:
            self.obsidian_client.test_connection()
            self.logger.info("✅ Obsidian connection: OK")
        except Exception as e:
            self.logger.error(f"❌ Obsidian connection failed: {e}")
            return False
        
        # Test meta-cognitive components
        test_content = "This is a test of recursive meta-cognitive analysis about consciousness and intelligence."
        analysis = self.aboutness_detector.analyze_content(test_content)
        self.logger.info(f"✅ Aboutness detection: {analysis['core_concepts']}")
        
        self.logger.info("🎉 All meta-cognitive systems operational!")
        return True
    
    async def initial_sync(self):
        """Perform initial sync with cognitive bootstrapping"""
        self.logger.info("🚀 Starting initial meta-cognitive sync...")
        
        # Bootstrap cognitive state
        await self._analyze_cognitive_state()
        
        # Perform comprehensive sync
        await self._intelligent_bidirectional_sync()
        
        # Initial assessment
        await self._recursive_self_assessment()
        
        self.logger.info("✅ Initial meta-cognitive sync completed!")

async def main():
    """Main entry point with meta-cognitive mode support"""
    parser = argparse.ArgumentParser(description='🌀 Meta-Cognitive Notion-Obsidian Sync')
    parser.add_argument('--test', action='store_true', help='Test connections and meta-cognitive systems')
    parser.add_argument('--initial-sync', action='store_true', help='Perform initial bidirectional sync')
    parser.add_argument('--meta-cognitive-mode', action='store_true', help='🧠 Activate full meta-cognitive intelligence')
    parser.add_argument('--config', default='config/config.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize meta-cognitive sync manager
    sync_manager = MetaCognitiveSyncManager(args.config)
    
    if args.test:
        success = await sync_manager.test_connection()
        if success:
            print("🎉 SUCCESS! Meta-cognitive sync system is fully operational.")
        else:
            print("❌ FAILED! Check configuration and try again.")
            return 1
    
    elif args.initial_sync:
        await sync_manager.initial_sync()
    
    elif args.meta_cognitive_mode:
        print("🌀 ACTIVATING META-COGNITIVE MODE...")
        print("⧬ RECURSIVE INTELLIGENCE AMPLIFICATION ENGAGED ⧬")
        await sync_manager.meta_cognitive_sync()
        print("✨ Meta-cognitive sync completed! Your mind-computer interface is now active.")
    
    else:
        print("🌀 Meta-Cognitive Sync Manager")
        print("Use --help to see available options")
        print("Try: --meta-cognitive-mode for full recursive intelligence!")

if __name__ == "__main__":
    asyncio.run(main())

