using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class LevelData
{
	public char[,] data;
}	

public class Levels : Singleton<Levels>
{
	public TextAsset data;
	
	public int current { get; set; }
	
	private List<LevelData> _levels;
	
	public int Count
	{
		get
		{
			if (_levels == null)
			{
				return 0;
			}
			else
			{
				return _levels.Count;
			}
		}
	}
	
	private void Start()
	{
		DontDestroyOnLoad(this);
	}
	
	public LevelData GetLevel(int number)
	{
		if (_loaded == false)
			Load();
		
		if (_levels == null || number >= _levels.Count)
			return null;
		else
			return _levels[number];
	}
	
	private bool _loaded = false;
	
	public void Load()
	{
		if (_loaded)
		{
			return;
		}
		
		_levels = new List<LevelData>();
		
		if (data == null)
		{
			data = Resources.Load("leveldata", typeof(TextAsset)) as TextAsset;
			
			if (data == null)
			{
				D.log("[Levels] level data is null!");
				return;	
			}
		}
		
		using (FastStringReader reader = new FastStringReader(data.text))
		{
			bool skip = false;
			while (!skip)
			{
				LevelData one = new LevelData();
				one.data = new char[G.rows, G.cols];
				for (int i = 0; i < G.rows; i++)
				{
					for (int j = 0; j < G.cols; j++)
					{
						one.data[i, j] = '-';
					}
				}
				
				// here's the big impact
				for (int i = 0; i < G.rowsInData; i++)
				{
					string line;
					
					line = reader.ReadLine();
					
					if (line == null)
					{
						D.log("[Levels] The data format is corrupted!");
						skip = true;
						break;
					}
					
					line = line.Trim().Replace(" ", "");
					
					for (int j = 0; j < line.Length; j++)
					{
						one.data[i, j] = line[j];
					}
				}
				
				if (!skip)
				{
					_levels.Add(one);
					
					// consume the blank line.
					string line = reader.ReadLine();
					if (line == null)
						skip = true;				
				}
			}
		}
		
		D.log("[Levels] {0} levels found.", _levels.Count);
		
		_loaded = true;
	}
}
