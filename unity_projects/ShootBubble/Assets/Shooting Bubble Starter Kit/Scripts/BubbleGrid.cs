using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class BubbleGrid : MonoBehaviour
{
	private Bubble[,] _grids;	
	private int _rows;
	private int _cols;
	
	private void Awake()
	{
		_rows = G.rows + 1;
		_cols = G.cols;
		
		_grids = new Bubble[_rows, _cols];
	}
	
	public Bubble Get(Index index)
	{
		return _grids[index.row, index.col];
	}
	
	public Bubble Get(int row, int col)
	{
		return _grids[row, col];
	}
	
	public void Set(Index index, Bubble bubble)
	{
		_grids[index.row, index.col] = bubble;
	}
	
	public void Set(int row, int col, Bubble bubble)
	{
		_grids[row, col] = bubble;
	}
	
	public void Remove(Index index)
	{
		_grids[index.row, index.col] = null;
	}
	
	public void Recalculate(LBRect rect)
	{
		for (int i = 0; i < _rows; i++)
		{
			for (int j = 0 ; j < _cols; j++)
			{
				var one = _grids[i, j];
				if (one != null)
				{
					one.transform.position = Misc.IndexToPosition(rect, new Index(i, j));
				}
			}
		}
	}
	
	public List<Bubble.Type> GetAllUniqueTypes()
	{
		List<Bubble.Type> all = new List<Bubble.Type>();
		
		for (int i = 0; i < G.rows; i++)
		{
			for (int j = 0; j < G.cols; j++)
			{
				var one = _grids[i, j];
				
				if (one != null)
				{
					Bubble.Type type = one.type;
					
					if (!all.Contains(type))
					{
						all.Add(type);
					}
				}
			}
		}
		
		return all;
	}
	
	public void Reset()
	{
		for (int i = 0; i < G.rows; i++)
		{
			for (int j = 0; j < G.cols; j++)
			{
				var one = _grids[i, j];
				if (one != null)
				{
					Destroy(one.gameObject);
					_grids[i, j] = null;
				}
			}
		}
	}
	
	public int Count
	{
		get
		{
			int sum = 0;
			for (int i = 0; i < _rows; i++)
			{
				for (int j = 0; j < _cols; j++)
				{
					if (_grids[i, j] != null)
					{
						sum++;
					}
				}
			}
			return sum;
		}
	}
	
	public int MaxRow
	{
		get
		{
			int max = -1;
			for (int i = 0; i < _rows; i++)
			{
				for (int j = 0; j < _cols; j++)
				{
					if (_grids[i, j] != null)
					{
						if (i > max)
						{
							max = i;
						}
					}
				}
			}
			return max;
		}
	}
}
