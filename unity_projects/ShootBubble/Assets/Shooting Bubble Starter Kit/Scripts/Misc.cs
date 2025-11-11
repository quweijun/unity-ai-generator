using UnityEngine;
using System.Collections;

public static class Misc
{
	/// <summary>
    /// Get the index from an approximate position.
    /// </summary>
    /// <returns>
    /// The index.
    /// </returns>
    /// <param name='position'>
    /// Approximate position.
    /// </param>
	public static Index PositionToIndex(LBRect bounds, Vector3 position)
	{
        float x = position.x - bounds.left;
        float y = position.y - bounds.bottom;
		
        int row;
        int col;

        row = Mathf.FloorToInt((bounds.height - G.radius - y + Mathf.Sqrt(3) / 2 * G.radius) / (Mathf.Sqrt(3) * G.radius));

        if (row % 2 == 0)
        {
        	if (x < 0)
        		x = 0;
        		
            col = Mathf.FloorToInt(x / (2 * G.radius));
        }
        else
        {
        	if (x < G.radius)
        		x = G.radius;
        	
            col = Mathf.FloorToInt((x - G.radius) / (2 * G.radius));

            // NOTE: we need to check whether col is _numberColumns - 1,
            // because in this case, half of the actual grid if out of the screen.
            // The actual reason behind this is that when our shooter's position is the
            // same as right bound, the above calculation would give us _numberColumns-1,
            // since we round things up a little bit, which means:
            //      x position      x index
            //          0               0
            //          2R              1
            //          19R             cols-1
            if (col >= G.cols - 1)
                col = G.cols - 2;
        }
		
        return new Index(row, col);
    }

    /// <summary>
    /// Get bubble's position from index.
    /// </summary>
    /// <returns>
    /// The bubble position.
    /// </returns>
    /// <param name='idx'>
    /// The index.
    /// </param>
    /// <param name='z'>
    /// Z.
    /// </param>
	public static Vector3 IndexToPosition(LBRect bounds, Index idx, float z = -1)
	{
        float x;
        float y;

        if (idx.row % 2 == 0)
            x = G.radius + 2 * G.radius * idx.col;
        else
            x = 2 * G.radius + 2 * G.radius * idx.col;

        y = bounds.height - G.radius - Mathf.Sqrt(3) * G.radius * idx.row;

		return new Vector3(x + bounds.left, y + bounds.bottom, z);
	}

	public static Index[] GetNeighbours(Index current)
	{
		int r = current.row;
		int c = current.col;
		
		// neighbouring indices are different according to their row index.
		//   for even row:
		//       (r-1, c-1) (r-1, c)
		//     (r, c-1) (r, c) (r, c+1)
		//       (r+1, c-1) (r+1, c)
		//
		//   for odd row:
		//       (r-1, c) (r-1, c+1)
		//     (r, c-1) (r, c) (r, c+1)
		//       (r+1, c) (r+1, c+1)
		if (r % 2 == 0) {
			// even
			return new Index[] {
				new Index(r - 1, c - 1),	new Index(r - 1, c),
				new Index(r, c - 1), 		new Index(r, c + 1),
				new Index(r + 1, c -1), 	new Index(r + 1, c)
			};
		} else {
			// odd
			return new Index[] {
				new Index(r - 1, c),		new Index(r - 1, c + 1),
				new Index(r, c - 1),		new Index(r, c + 1),
				new Index(r + 1, c),		new Index(r + 1, c + 1)
			};
		}
	}
	
}
