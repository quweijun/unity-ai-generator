using UnityEngine;
using System.Collections;

/// <summary>
/// Use row and col is much more clear.
/// The origin of row and col starts from the upper left.  
/// </summary>
public struct Index
{
	public Index(int row, int col) {
        this.row = row;
        this.col = col;
	}
	
	public int row;
	public int col;
}
