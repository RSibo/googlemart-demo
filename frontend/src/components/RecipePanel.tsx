import React from 'react';
import type { Recipe } from '../types';

interface RecipePanelProps {
  recipe: Recipe;
  onClose: () => void;
}

const RecipePanel: React.FC<RecipePanelProps> = ({ recipe, onClose }) => {
  return (
    <div style={{
      position: 'fixed',
      left: '50%',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      width: '90%',
      maxWidth: '600px',
      maxHeight: '80vh',
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
      zIndex: 2000,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <div style={{ background: '#00875a', color: 'white', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>{recipe.name}</h2>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' }}>&times;</button>
      </div>
      
      <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
        {recipe.prep_time && <p><strong>Prep Time:</strong> {recipe.prep_time}</p>}
        
        <h3>Ingredients</h3>
        <ul>
          {recipe.ingredients.map((ing, i) => (
            <li key={i}>{ing}</li>
          ))}
        </ul>
        
        <h3>Instructions</h3>
        <p style={{ whiteSpace: 'pre-wrap' }}>{recipe.instructions}</p>
      </div>
      
      <div style={{ padding: '20px', borderTop: '1px solid #eee', textAlign: 'right' }}>
        <button 
          onClick={onClose}
          style={{ padding: '10px 20px', borderRadius: '4px', border: '1px solid #ccc', background: 'white', cursor: 'pointer', marginRight: '10px' }}
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default RecipePanel;
