"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    bids = data['bids']
    if len({b['agent'] for b in bids}) != len(bids) or any(b['bid'] < 0 or b['budget'] < b['bid'] for b in bids):
        raise ValueError('Each bidder needs a unique ID and enough declared budget')
    eligible = sorted((b for b in bids if b['bid'] >= data['reserve']), key=lambda b: (-b['bid'], b['agent']))
    if not eligible:
        return {'winner': None, 'price': None, 'cleared': False}
    price = max(data['reserve'], eligible[1]['bid'] if len(eligible) > 1 else data['reserve'])
    allocation = {'winner': eligible[0]['agent'], 'price': price, 'winning_bid': eligible[0]['bid'], 'mechanism': 'sealed-bid second-price, one slot'}
    explanation = await agent.ask('explain_auction', 'Explain this resource allocation and the payment rule. Do not claim actual money moved.', allocation,
                                 'Agent a wins with a bid of 30 and pays the second-highest eligible bid, 25. This is a local allocation simulation.')
    return {**allocation, 'cleared': True, 'explanation': explanation}
