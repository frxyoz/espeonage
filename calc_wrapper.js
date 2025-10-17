#!/usr/bin/env node

/**
 * Wrapper script for @smogon/calc damage calculator
 * Reads JSON input from stdin and outputs calculation results
 */

const { calculate, Generations, Pokemon, Move, Field } = require('@smogon/calc');

// Read input from stdin
let inputData = '';

process.stdin.on('data', (chunk) => {
  inputData += chunk;
});

process.stdin.on('end', () => {
  try {
    const input = JSON.parse(inputData);
    
    // Get the generation (default to 9 for latest)
    const gen = Generations.get(input.gen || 9);
    
    // Create attacker Pokémon
    const attacker = new Pokemon(gen, input.attacker.species, {
      level: input.attacker.level || 100,
      ability: input.attacker.ability,
      item: input.attacker.item,
      nature: input.attacker.nature,
      evs: input.attacker.evs,
      ivs: input.attacker.ivs,
    });
    
    // Create defender Pokémon
    const defender = new Pokemon(gen, input.defender.species, {
      level: input.defender.level || 100,
      ability: input.defender.ability,
      item: input.defender.item,
      nature: input.defender.nature,
      evs: input.defender.evs,
      ivs: input.defender.ivs,
    });
    
    // Create move
    const move = new Move(gen, input.move);
    
    // Create field (optional)
    const field = input.field ? new Field(input.field) : new Field();
    
    // Calculate damage
    const result = calculate(gen, attacker, defender, move, field);
    
    // Format output
    const output = {
      damage: result.damage,
      damageRange: result.range(),
      description: result.fullDesc(),
      kochance: result.kochance(),
    };
    
    console.log(JSON.stringify(output, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
});
