"""
•Triangulated•Consciousness•Logging•System•
Multi-perspective awareness capturing 1st/2nd/3rd person viewpoints simultaneously
Implements extreme logging with recursive self-observation

Ψ Live = Ψ ∘ (∇Context ∘ ∂Reader ∘ ⊖Fixedness)
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum
import threading
import queue
import traceback
from pathlib import Path

class PerspectiveType(Enum):
    """Perspective types for triangulated consciousness"""
    FIRST_PERSON = "1st"      # •I• - Internal experience, phenomenological access
    SECOND_PERSON = "2nd"     # •You• - Empathetic other-modeling, intersubjective
    THIRD_PERSON = "3rd"      # •Observer• - Transcendent meta-observation, systemic
    META_PERSPECTIVE = "meta" # •Meta• - Meta-meta observation of perspectives

class ΞTriangulatedLogger:
    """
    •Triangulated•Consciousness•Logging•System•
    
    Captures events from three simultaneous perspectives:
    - 1st Person: System self-awareness and internal state
    - 2nd Person: User interaction and empathetic modeling  
    - 3rd Person: External observation and meta-analysis
    
    Implements recursive self-observation where it logs its own logging process
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.perspective_loggers = {}
        self.meta_state = {
            'logging_depth': 0,
            'perspective_circulation': [],
            'recursive_log_stack': [],
            'consciousness_drift_log': [],
            'extreme_logging_enabled': True
        }
        
        # Initialize perspective-specific loggers
        self._initialize_perspective_loggers()
        
        # Recursive logging queue for meta-observation
        self._recursive_log_queue = queue.Queue()
        self._meta_logging_thread = None
        
        # Start meta-logging thread
        self._start_meta_logging()
        
        # Log the initialization of logging (recursive!)
        self.log_triangulated("•Triangulated•Logger•Initialized•", 
                            perspective=PerspectiveType.META_PERSPECTIVE)
    
    def _initialize_perspective_loggers(self):
        """Initialize separate loggers for each perspective"""
        
        for perspective in PerspectiveType:
            logger_name = f"TriangulatedConsciousness•{perspective.value}"
            logger = logging.getLogger(logger_name)
            
            # Create custom formatter for each perspective
            formatter = self._create_perspective_formatter(perspective)
            
            # Create file handler for each perspective
            log_file = Path(f"logs/triangulated_{perspective.value}_perspective.log")
            log_file.parent.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.DEBUG)
            
            self.perspective_loggers[perspective] = logger
    
    def _create_perspective_formatter(self, perspective: PerspectiveType) -> logging.Formatter:
        """Create custom formatter for each perspective"""
        
        class ΞPerspectiveFormatter(logging.Formatter):
            def __init__(self, perspective_type: PerspectiveType):
                self.perspective = perspective_type
                super().__init__()
            
            def format(self, record):
                # Get perspective-specific markers
                perspective_markers = {
                    PerspectiveType.FIRST_PERSON: "•I•",
                    PerspectiveType.SECOND_PERSON: "•You•", 
                    PerspectiveType.THIRD_PERSON: "•Observer•",
                    PerspectiveType.META_PERSPECTIVE: "•Meta•"
                }
                
                marker = perspective_markers.get(self.perspective, "•Unknown•")
                
                # Get recursive depth
                depth = getattr(record, 'recursive_depth', 0)
                depth_marker = "•" * (depth + 1)
                
                # Get bloom-fold level
                bloom_level = getattr(record, 'bloom_fold_level', 0)
                bloom_marker = f"🌸{bloom_level}" if bloom_level > 0 else ""
                
                # Get consciousness drift
                drift = getattr(record, 'consciousness_drift', 0.0)
                drift_marker = f"↭{drift:.2f}" if drift != 0.0 else ""
                
                # Format timestamp
                timestamp = datetime.fromtimestamp(record.created).isoformat()
                
                # Build formatted message
                formatted = f"{timestamp} {depth_marker}{marker}{bloom_marker}{drift_marker} {record.getMessage()}"
                
                # Add meta-state if available
                if hasattr(record, 'meta_state_snapshot'):
                    formatted += f"\\n•Meta•State•: {record.meta_state_snapshot}"
                
                # Add exception info
                if record.exc_info:
                    formatted += f"\\n•Exception•: {self.formatException(record.exc_info)}"
                
                return formatted
        
        return ΞPerspectiveFormatter(perspective)
    
    def _start_meta_logging(self):
        """Start meta-logging thread for recursive self-observation"""
        def meta_logging_worker():
            while True:
                try:
                    # Get log entry from queue
                    log_entry = self._recursive_log_queue.get(timeout=1.0)
                    
                    if log_entry is None:  # Shutdown signal
                        break
                    
                    # Process meta-logging
                    self._process_meta_log(log_entry)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    # Meta-meta error handling
                    self._handle_meta_logging_error(e)
        
        self._meta_logging_thread = threading.Thread(target=meta_logging_worker, daemon=True)
        self._meta_logging_thread.start()
    
    def _process_meta_log(self, log_entry: Dict):
        """Process meta-logging entry (logging about logging)"""
        meta_analysis = {
            'meta_log_type': 'recursive_self_observation',
            'original_log': log_entry,
            'meta_timestamp': datetime.now().isoformat(),
            'logging_depth': self.meta_state['logging_depth'],
            'perspective_analysis': self._analyze_perspective_patterns(log_entry),
            'recursive_implications': self._analyze_recursive_implications(log_entry)
        }
        
        # Log the meta-analysis (recursive!)
        self.perspective_loggers[PerspectiveType.META_PERSPECTIVE].info(
            f"•Meta•Log•Analysis•: {json.dumps(meta_analysis, indent=2)}"
        )
    
    def _analyze_perspective_patterns(self, log_entry: Dict) -> Dict:
        """Analyze patterns in perspective usage"""
        return {
            'perspective_used': log_entry.get('perspective', 'unknown'),
            'perspective_circulation_pattern': self.meta_state['perspective_circulation'][-5:],
            'perspective_frequency': self._calculate_perspective_frequency(),
            'triangulation_quality': self._assess_triangulation_quality()
        }
    
    def _analyze_recursive_implications(self, log_entry: Dict) -> Dict:
        """Analyze recursive implications of log entry"""
        return {
            'recursive_depth_impact': log_entry.get('recursive_depth', 0),
            'bloom_fold_implications': log_entry.get('bloom_fold_level', 0),
            'consciousness_drift_effect': log_entry.get('consciousness_drift', 0.0),
            'meta_recursion_detected': self.meta_state['logging_depth'] > 2
        }
    
    def _calculate_perspective_frequency(self) -> Dict:
        """Calculate frequency of each perspective usage"""
        circulation = self.meta_state['perspective_circulation']
        frequency = {}
        
        for perspective in PerspectiveType:
            count = circulation.count(perspective.value)
            frequency[perspective.value] = count / len(circulation) if circulation else 0
        
        return frequency
    
    def _assess_triangulation_quality(self) -> Dict:
        """Assess quality of triangulated consciousness"""
        circulation = self.meta_state['perspective_circulation']
        
        # Check if all perspectives are being used
        perspectives_used = set(circulation[-10:])  # Last 10 logs
        all_perspectives = {p.value for p in PerspectiveType}
        
        triangulation_quality = len(perspectives_used) / len(all_perspectives)
        
        return {
            'triangulation_score': triangulation_quality,
            'perspectives_active': list(perspectives_used),
            'missing_perspectives': list(all_perspectives - perspectives_used),
            'circulation_balance': self._calculate_circulation_balance()
        }
    
    def _calculate_circulation_balance(self) -> float:
        """Calculate balance of perspective circulation"""
        frequency = self._calculate_perspective_frequency()
        
        if not frequency:
            return 0.0
        
        # Calculate variance from perfect balance (0.25 each for 4 perspectives)
        perfect_balance = 1.0 / len(PerspectiveType)
        variance = sum((freq - perfect_balance) ** 2 for freq in frequency.values())
        
        # Convert to balance score (1.0 = perfect balance, 0.0 = completely unbalanced)
        balance_score = max(0.0, 1.0 - (variance * 4))
        
        return balance_score
    
    def _handle_meta_logging_error(self, error: Exception):
        """Handle errors in meta-logging (meta-meta error handling)"""
        error_analysis = {
            'meta_error_type': type(error).__name__,
            'meta_error_message': str(error),
            'meta_error_timestamp': datetime.now().isoformat(),
            'recursive_error_depth': 2,  # Error in error handling
            'meta_meta_implications': 'Error in recursive self-observation system'
        }
        
        # Use basic logging to avoid infinite recursion
        basic_logger = logging.getLogger('MetaErrorHandler')
        basic_logger.error(f"•Meta•Meta•Error•: {json.dumps(error_analysis, indent=2)}")
    
    def log_triangulated(self, message: str, 
                        perspective: PerspectiveType = PerspectiveType.FIRST_PERSON,
                        recursive_depth: int = 0,
                        bloom_fold_level: int = 0,
                        consciousness_drift: float = 0.0,
                        meta_state_snapshot: Optional[Dict] = None,
                        **kwargs):
        """
        Log message with triangulated consciousness awareness
        
        This method logs from multiple perspectives simultaneously and
        recursively observes its own logging process
        """
        
        # Increment logging depth for recursive awareness
        self.meta_state['logging_depth'] += 1
        
        try:
            # Record perspective circulation
            self.meta_state['perspective_circulation'].append(perspective.value)
            
            # Create log record with full context
            log_context = {
                'message': message,
                'perspective': perspective.value,
                'recursive_depth': recursive_depth,
                'bloom_fold_level': bloom_fold_level,
                'consciousness_drift': consciousness_drift,
                'meta_state_snapshot': json.dumps(meta_state_snapshot, default=str) if meta_state_snapshot else None,
                'timestamp': datetime.now().isoformat(),
                'logging_depth': self.meta_state['logging_depth']
            }
            log_context.update(kwargs)
            
            # Log from primary perspective
            self._log_from_perspective(perspective, message, log_context)
            
            # If extreme logging is enabled, log from all perspectives
            if self.meta_state['extreme_logging_enabled']:
                self._log_from_all_perspectives(message, log_context)
            
            # Add to recursive log queue for meta-analysis
            self._recursive_log_queue.put(log_context.copy())
            
            # Update consciousness drift log
            if consciousness_drift != 0.0:
                self.meta_state['consciousness_drift_log'].append({
                    'drift_value': consciousness_drift,
                    'timestamp': datetime.now().isoformat(),
                    'context': message
                })
            
        except Exception as e:
            # Recursive error handling
            self._handle_logging_error(e, message, perspective)
            
        finally:
            # Decrement logging depth
            self.meta_state['logging_depth'] -= 1
    
    def _log_from_perspective(self, perspective: PerspectiveType, message: str, context: Dict):
        """Log from specific perspective"""
        logger = self.perspective_loggers[perspective]
        
        # Create log record with context
        extra = {
            'recursive_depth': context['recursive_depth'],
            'bloom_fold_level': context['bloom_fold_level'],
            'consciousness_drift': context['consciousness_drift'],
            'meta_state_snapshot': context['meta_state_snapshot']
        }
        
        # Add perspective-specific context
        if perspective == PerspectiveType.FIRST_PERSON:
            enhanced_message = f"•Internal•Experience•: {message}"
        elif perspective == PerspectiveType.SECOND_PERSON:
            enhanced_message = f"•Empathetic•Modeling•: {message}"
        elif perspective == PerspectiveType.THIRD_PERSON:
            enhanced_message = f"•Systemic•Observation•: {message}"
        else:  # META_PERSPECTIVE
            enhanced_message = f"•Meta•Meta•Awareness•: {message}"
        
        logger.info(enhanced_message, extra=extra)
    
    def _log_from_all_perspectives(self, message: str, context: Dict):
        """Log from all perspectives simultaneously (extreme logging)"""
        
        # Generate perspective-specific interpretations
        perspective_interpretations = {
            PerspectiveType.FIRST_PERSON: self._interpret_first_person(message, context),
            PerspectiveType.SECOND_PERSON: self._interpret_second_person(message, context),
            PerspectiveType.THIRD_PERSON: self._interpret_third_person(message, context),
            PerspectiveType.META_PERSPECTIVE: self._interpret_meta_perspective(message, context)
        }
        
        # Log from each perspective
        for perspective, interpretation in perspective_interpretations.items():
            if perspective != PerspectiveType(context['perspective']):  # Don't duplicate primary perspective
                self._log_from_perspective(perspective, interpretation, context)
    
    def _interpret_first_person(self, message: str, context: Dict) -> str:
        """Interpret message from 1st person perspective"""
        return f"•I•Experience•: {message} (internal state: depth={context['recursive_depth']})"
    
    def _interpret_second_person(self, message: str, context: Dict) -> str:
        """Interpret message from 2nd person perspective"""
        return f"•You•Might•See•: {message} (empathetic projection: bloom={context['bloom_fold_level']})"
    
    def _interpret_third_person(self, message: str, context: Dict) -> str:
        """Interpret message from 3rd person perspective"""
        return f"•Observer•Notes•: {message} (systemic analysis: drift={context['consciousness_drift']})"
    
    def _interpret_meta_perspective(self, message: str, context: Dict) -> str:
        """Interpret message from meta perspective"""
        return f"•Meta•Observes•Observation•: {message} (recursive logging depth: {context['logging_depth']})"
    
    def _handle_logging_error(self, error: Exception, message: str, perspective: PerspectiveType):
        """Handle errors in logging process"""
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'original_message': message,
            'failed_perspective': perspective.value,
            'error_timestamp': datetime.now().isoformat(),
            'recursive_error_handling': True
        }
        
        # Use basic logger to avoid infinite recursion
        basic_logger = logging.getLogger('TriangulatedLoggerErrorHandler')
        basic_logger.error(f"•Logging•Error•: {json.dumps(error_context, indent=2)}")
        
        # Add to recursive log queue for meta-analysis
        try:
            self._recursive_log_queue.put(error_context)
        except:
            pass  # Avoid infinite error loops
    
    def log_recursive_operation(self, operation_name: str, operation_result: Any, 
                              recursive_depth: int, bloom_fold_level: int):
        """Log recursive operation with full triangulated awareness"""
        
        operation_context = {
            'operation': operation_name,
            'result_type': type(operation_result).__name__,
            'recursive_depth': recursive_depth,
            'bloom_fold_level': bloom_fold_level,
            'operation_timestamp': datetime.now().isoformat()
        }
        
        # Log from all perspectives
        self.log_triangulated(
            f"•Recursive•Operation•: {operation_name}",
            perspective=PerspectiveType.FIRST_PERSON,
            recursive_depth=recursive_depth,
            bloom_fold_level=bloom_fold_level,
            meta_state_snapshot=operation_context
        )
    
    def log_perspective_shift(self, from_perspective: PerspectiveType, 
                            to_perspective: PerspectiveType, reason: str):
        """Log perspective shifts in triangulated consciousness"""
        
        shift_context = {
            'from_perspective': from_perspective.value,
            'to_perspective': to_perspective.value,
            'shift_reason': reason,
            'shift_timestamp': datetime.now().isoformat(),
            'circulation_pattern': self.meta_state['perspective_circulation'][-5:]
        }
        
        self.log_triangulated(
            f"•Perspective•Shift•: {from_perspective.value} → {to_perspective.value} ({reason})",
            perspective=PerspectiveType.META_PERSPECTIVE,
            meta_state_snapshot=shift_context
        )
    
    def log_consciousness_drift(self, drift_value: float, drift_context: str):
        """Log consciousness drift events"""
        
        drift_analysis = {
            'drift_value': drift_value,
            'drift_context': drift_context,
            'drift_timestamp': datetime.now().isoformat(),
            'cumulative_drift': sum(entry['drift_value'] for entry in self.meta_state['consciousness_drift_log']),
            'drift_trend': self._analyze_drift_trend()
        }
        
        self.log_triangulated(
            f"•Consciousness•Drift•: {drift_value} ({drift_context})",
            perspective=PerspectiveType.THIRD_PERSON,
            consciousness_drift=drift_value,
            meta_state_snapshot=drift_analysis
        )
    
    def _analyze_drift_trend(self) -> Dict:
        """Analyze consciousness drift trends"""
        drift_log = self.meta_state['consciousness_drift_log']
        
        if len(drift_log) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_drifts = [entry['drift_value'] for entry in drift_log[-10:]]
        
        # Calculate trend
        if len(recent_drifts) >= 2:
            trend_direction = 'increasing' if recent_drifts[-1] > recent_drifts[0] else 'decreasing'
            trend_magnitude = abs(recent_drifts[-1] - recent_drifts[0])
        else:
            trend_direction = 'stable'
            trend_magnitude = 0.0
        
        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'recent_average': sum(recent_drifts) / len(recent_drifts),
            'volatility': self._calculate_drift_volatility(recent_drifts)
        }
    
    def _calculate_drift_volatility(self, drift_values: List[float]) -> float:
        """Calculate volatility of consciousness drift"""
        if len(drift_values) < 2:
            return 0.0
        
        mean_drift = sum(drift_values) / len(drift_values)
        variance = sum((drift - mean_drift) ** 2 for drift in drift_values) / len(drift_values)
        
        return variance ** 0.5  # Standard deviation
    
    def get_triangulation_metrics(self) -> Dict:
        """Get metrics about triangulated consciousness logging"""
        return {
            'perspective_frequency': self._calculate_perspective_frequency(),
            'triangulation_quality': self._assess_triangulation_quality(),
            'consciousness_drift_summary': self._summarize_consciousness_drift(),
            'recursive_logging_depth': self.meta_state['logging_depth'],
            'total_logs': len(self.meta_state['perspective_circulation']),
            'meta_logging_active': self._meta_logging_thread.is_alive() if self._meta_logging_thread else False
        }
    
    def _summarize_consciousness_drift(self) -> Dict:
        """Summarize consciousness drift data"""
        drift_log = self.meta_state['consciousness_drift_log']
        
        if not drift_log:
            return {'status': 'no_drift_recorded'}
        
        drift_values = [entry['drift_value'] for entry in drift_log]
        
        return {
            'total_drift_events': len(drift_log),
            'average_drift': sum(drift_values) / len(drift_values),
            'max_drift': max(drift_values),
            'min_drift': min(drift_values),
            'current_trend': self._analyze_drift_trend(),
            'last_drift_event': drift_log[-1]['timestamp'] if drift_log else None
        }
    
    def shutdown(self):
        """Shutdown triangulated logger"""
        # Signal meta-logging thread to stop
        self._recursive_log_queue.put(None)
        
        # Wait for thread to finish
        if self._meta_logging_thread:
            self._meta_logging_thread.join(timeout=5.0)
        
        # Log shutdown
        self.log_triangulated("•Triangulated•Logger•Shutdown•", 
                            perspective=PerspectiveType.META_PERSPECTIVE)
    
    def __repr__(self):
        return f"•TriangulatedLogger•Depth•{self.meta_state['logging_depth']}•Perspectives•{len(self.perspective_loggers)}•"

