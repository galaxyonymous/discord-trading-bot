"""
Signal Parser for Discord Trading Signals
Parses messages in the format:
Buying $SYMBOL
First buying: price-range
Second buying: price
CMP: price
Targets: percentages
SL: price
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TradingSignal:
    """Represents a parsed trading signal"""
    symbol: str
    first_buy_range: Tuple[float, float]  # (min, max)
    second_buy: float
    cmp: float  # Current Market Price
    targets: List[float]  # List of target percentages
    stop_loss: float
    
    def __str__(self):
        return f"""
Trading Signal:
Symbol: {self.symbol}
First Buy Range: {self.first_buy_range[0]} - {self.first_buy_range[1]}
Second Buy: {self.second_buy}
CMP: {self.cmp}
Targets: {self.targets}%
Stop Loss: {self.stop_loss}
"""


class SignalParser:
    """Parses trading signals from Discord messages"""
    
    @staticmethod
    def parse_message(message_content: str) -> Optional[TradingSignal]:
        """
        Parse a Discord message and extract trading signal information.
        
        Args:
            message_content: The content of the Discord message
            
        Returns:
            TradingSignal object if parsing successful, None otherwise
        """
        try:
            # Extract symbol (e.g., $LSK, $BTC)
            symbol_match = re.search(r'\$([A-Z0-9]+)', message_content, re.IGNORECASE)
            if not symbol_match:
                return None
            
            symbol = symbol_match.group(1).upper()
            
            # Extract first buying range (e.g., "0.208– 0.210" or "0.208-0.210")
            first_buy_match = re.search(
                r'first\s+buying[:\s]+([\d.]+)[\s–-]+([\d.]+)', 
                message_content, 
                re.IGNORECASE
            )
            if not first_buy_match:
                return None
            
            first_buy_min = float(first_buy_match.group(1))
            first_buy_max = float(first_buy_match.group(2))
            
            # Extract second buying price
            second_buy_match = re.search(
                r'second\s+buying[:\s]+([\d.]+)', 
                message_content, 
                re.IGNORECASE
            )
            if not second_buy_match:
                return None
            
            second_buy = float(second_buy_match.group(1))
            
            # Extract CMP (Current Market Price)
            cmp_match = re.search(
                r'cmp[:\s]+([\d.]+)', 
                message_content, 
                re.IGNORECASE
            )
            if not cmp_match:
                return None
            
            cmp = float(cmp_match.group(1))
            
            # Extract targets (percentages)
            targets = []
            target_matches = re.findall(
                r'(\d+)%', 
                message_content
            )
            for match in target_matches:
                targets.append(float(match))
            
            if not targets:
                # Try alternative format
                target_section = re.search(
                    r'targets?\s*[:\n]+([\d%\s,]+)', 
                    message_content, 
                    re.IGNORECASE
                )
                if target_section:
                    target_values = re.findall(r'(\d+)%', target_section.group(1))
                    targets = [float(t) for t in target_values]
            
            # Extract stop loss
            sl_match = re.search(
                r'sl[:\s]+([\d.]+)', 
                message_content, 
                re.IGNORECASE
            )
            if not sl_match:
                return None
            
            stop_loss = float(sl_match.group(1))
            
            return TradingSignal(
                symbol=symbol,
                first_buy_range=(first_buy_min, first_buy_max),
                second_buy=second_buy,
                cmp=cmp,
                targets=sorted(targets),  # Sort targets in ascending order
                stop_loss=stop_loss
            )
            
        except Exception as e:
            print(f"Error parsing signal: {e}")
            return None
    
    @staticmethod
    def is_signal_message(message_content: str) -> bool:
        """
        Check if a message looks like a trading signal.
        
        Args:
            message_content: The content of the Discord message
            
        Returns:
            True if message appears to be a trading signal
        """
        # Check for key indicators
        has_symbol = bool(re.search(r'\$[A-Z0-9]+', message_content, re.IGNORECASE))
        has_buying = bool(re.search(r'buying', message_content, re.IGNORECASE))
        has_cmp = bool(re.search(r'cmp', message_content, re.IGNORECASE))
        has_targets = bool(re.search(r'\d+%', message_content))
        has_sl = bool(re.search(r'sl[:\s]+[\d.]+', message_content, re.IGNORECASE))
        
        return has_symbol and has_buying and (has_cmp or has_targets or has_sl)

