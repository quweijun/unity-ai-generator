using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.SceneManagement;


public class BubbleManager : MonoBehaviour {

	#region Prefabs
	public GameObject ball = null;
	public GameObject cannon = null;
	#endregion

	public GameObject compressor;
	private int _compressorLevel;
	private int GlobalLevel = 0;
	private GameObject winPanel;
	private GameObject failPanel;
	private int startgameflag = 0;
	private float timer = 0;
	public int totalscore = 0;
	public int levelscore = 0;
	public Text totalScoreText;
	public Text totalLevelText; 


	public int timeBeforeNewRoot = 3;
	private int _newRoot;
	
	public float collisionEpsilon = 0.82f;
	
	private BubbleGrid _grid;
	
	private Bubble _shooter = null;
	private float _shootingAngle = 90.0f;
	
	private Bubble _next;
	
	private bool _fired = false;

	private LBRect _boundRect;
	
	#region :: Sound ::
	public AudioClip destroyGroupClip;
	public AudioClip hurryClip;
	public AudioClip launchClip;
	public AudioClip loseClip;
	public AudioClip newRootSoloClip;
	public AudioClip nohClip;
	public AudioClip reboundClip;
	public AudioClip stickClip;
	#endregion

	#region :: Bubbles ::
	public Sprite _bubble_1;
	public Sprite _bubble_2;
	public Sprite _bubble_3;
	public Sprite _bubble_4;
	public Sprite _bubble_5;
	public Sprite _bubble_6;
	public Sprite _bubble_7;
	public Sprite _bubble_8;
	#endregion

	#region :: Cached Internal Variables ::
    // cached variables in Update()
    private float _dx;
    private float _dy;

    // cached usage in GetChain()
	private bool[,] _visited;
	#endregion
	
	private enum RemoveType {
		ChainRemoval,
		UnlinkRemoval
	}
	
	void Start ()
	{
		this.winPanel=GameObject.Find("WinPanel");
		this.failPanel = GameObject.Find("FailPanel");
		this.winPanel.SetActive(false);
		this.failPanel.SetActive(false);

		_grid = this.GetComponent<BubbleGrid>();
	
		_visited = new bool[G.rows, G.cols];
		
		cannon.transform.position = GetShooterPosition();
		
		LoadNextLevel();
	}

	/*
	 * 加载下一关
	 */
	public void LoadNextLevel(int currLevel=0)
	{
		this.levelscore = 0;
		Levels.Instance.current++;

		if (_next != null)
		{
			Destroy(_next.gameObject);
			_next = null;		
		}
		if (_shooter != null)
		{
			Destroy(_shooter.gameObject);
			_shooter = null;		
		}
		
		_newRoot = 0;

		float realWidth = G.cols * G.radius * 2.0f;
		float realHeight = Mathf.Sqrt(3.0f) * (G.rows - 1) * G.radius + 2 * G.radius;
		
        _boundRect = new LBRect(-realWidth / 2.0f, -realHeight / 2.0f, realWidth, realHeight);

		iTween.Stop(compressor);
		compressor.transform.position = new Vector3(0, _boundRect.top, -1);
		_compressorLevel = 0;
		
		// load first
		Levels.Instance.Load();
		/*
		 *获取游戏关卡 begin
		 */
		LevelData ld = null;
		if (currLevel==0)
			{
				int number = Random.Range(0, Levels.Instance.Count - 1);
				ld = Levels.Instance.GetLevel(number);
				this.GlobalLevel = number;
			}
		else
			{
			ld = Levels.Instance.GetLevel(currLevel);
		}
		//Debug.Log(this.GlobalLevel);
		//获取游戏关卡 end
		_grid.Reset();
		
		if (ld != null)
		{
			for (int i = 0; i < G.rows; i++)
			{
				for (int j = 0; j < G.cols; j++)
				{
					char ch = ld.data[i, j];
					if (ch != '-')
					{
						Bubble one = GetOneBubbleAtPosition(Misc.IndexToPosition(_boundRect, new Index(i, j)), Bubble.CharToType(ch));
						_grid.Set(i, j, one);
					}
				}
			}
		}
		
		// initialize the shooter初始化射击球
		//if (this.startgameflag == 1) { 
		  LoadShooterBubble();
		//}
		this.startgameflag = 1;
	}
	
	void Update ()
	{
		//如果开始标志为0则退出
		//Debug.Log(this.startgameflag);
		if (this.startgameflag == 0)
		{
			timer = 0;
			return;
		}
		
		timer += Time.deltaTime;	
		if (timer<0.3)
        {
			return;
        }

		this.totalScoreText.text = "Total:"+this.totalscore.ToString();
		this.totalLevelText.text = "Score:"+this.levelscore.ToString();

		if (!_fired) {
#if UNITY_EDITOR
			if (Input.GetMouseButtonUp(0))
			{
				Finger f = new Finger();
				f.x = Input.mousePosition.x;
				f.y = Input.mousePosition.y;
				
				HandleTouchBegan(f);
				HandleTouchEnded(f);
			}
#endif

#if UNITY_IPHONE || UNITY_ANDROID
			if (Input.touchCount > 0) {
				Touch touch = Input.GetTouch(0);
				
				Finger f = new Finger();
				f.x = touch.position.x;
				f.y = touch.position.y;
				
				if (touch.phase == TouchPhase.Began)
					HandleTouchBegan(f);
				if (touch.phase == TouchPhase.Moved)
					HandleTouchMoved(f);
				if (touch.phase == TouchPhase.Ended)
					HandleTouchEnded(f);
				if (touch.phase == TouchPhase.Canceled)
					HandleTouchCanceled(f);
			}
#else
			// mimic the touch event on Desktop platform
			if (Input.GetMouseButtonDown(0)) {
				Finger f = new Finger();
				f.x = Input.mousePosition.x;
				f.y = Input.mousePosition.y;

				HandleTouchBegan(f);
			} else if (Input.GetMouseButtonUp(0)) {
				Finger f = new Finger();
				f.x = Input.mousePosition.x;
				f.y = Input.mousePosition.y;

				HandleTouchEnded(f);
			} else if (Input.GetMouseButton(0)) {
				Finger f = new Finger();
				f.x = Input.mousePosition.x;
				f.y = Input.mousePosition.y;

				HandleTouchMoved(f);
			}
#endif
		}

		if (_fired) {
            Vector3 position = _shooter.transform.position;

            float x = position.x;
            float y = position.y;

            ParkingStateInfo info = IsFinalParkingIndex(G.bubbleSpeed, collisionEpsilon, x, y, _dx, _dy, true);

            _dx = info.dx;
            _dy = info.dy;

            x = info.x;
            y = info.y;

            if (info.final)
            {
                ParkBubble(new Vector3(x, y));                
			}
			else
			{
	            _shooter.transform.position = new Vector3(x, y, position.z);
	        }

			WinOrLose();
		}
	}

	/*
	 * 开火
	 */
    private void StartFire()
    {
        _fired = true;

        _dx = Mathf.Cos(_shootingAngle * Mathf.Deg2Rad);
        _dy = Mathf.Sin(_shootingAngle * Mathf.Deg2Rad);

		AudioManager.Instance.Play(launchClip);
    }

	private bool IsCollidingOthers(Vector3 shooterPosition, float epsilon)
	{
		// collision check from bottom to top
		for (int i = G.rows - 1; i >= 0; i--) {
			for (int j = 0; j < G.cols; j++) {
				var other = _grid.Get(i, j);
				if (other != null) {
					var otherPosition = other.transform.position;
					
					if (IsCloseEnough(shooterPosition, otherPosition, epsilon)) {
						return true;
					}						
				}
			}
		}
		
		return false;
	}
	
	/*
	 * 停球
	 */
	private void ParkBubble(Vector3 currentPosition)
	{
		Index index = Misc.PositionToIndex(_boundRect, currentPosition);
		Vector3 position = Misc.IndexToPosition(_boundRect, index);
		
		if (_grid.Get(index) != null)
        {
            D.log("The index ({0}, {1}) should be null, got from position ({2}, {3}).",
                index.row, index.col, currentPosition.x, currentPosition.y);
			return;
		}
		
		if (index.row + _compressorLevel >= G.rows)
		{
			// we lose
			loseCallback();
			return;
		}
		
		_shooter.transform.position = position;
		_grid.Set(index, _shooter);
		
        OnChain(index);

        OnUnlink(index);

		_newRoot++;
		if (_newRoot == timeBeforeNewRoot - 1)
		{
			// shake compressor
			iTween.ShakePosition(compressor, iTween.Hash("x", 5.0f, "y", 5.0f, "time", 1.0f, "looptype", "loop"));
		}
		else if (_newRoot > timeBeforeNewRoot)
		{
			_newRoot = 0;

			AudioManager.Instance.Play(newRootSoloClip);
			
			iTween.Stop(compressor);			

			float delta = Mathf.Sqrt(3.0f) * G.radius;
			compressor.transform.MoveBy(0, -delta, 0);
			_compressorLevel++;
			
			// recalculate the bubbles' positions
			_boundRect.top -= delta;
			_grid.Recalculate(_boundRect);
		}
		
		LoadShooterBubble();
	}
	
	/*
	 * 移除球
	 */
	private void RemoveBubbles(List<Index> bubbles, RemoveType type)
	{
		for (int i = 0; i < bubbles.Count; i++)
		{
			var b = _grid.Get(bubbles[i]);
			
			if (type == RemoveType.UnlinkRemoval)
			{
				FallEffect fall = b.gameObject.AddComponent<FallEffect>();
				fall.gravity = 1500.0f;
				fall.initialAngle = 0;
				fall.initialVelocity = 0;
				fall.lowerLimit = _boundRect.bottom;				
			}
			else
			{
				FallEffect fall = b.gameObject.AddComponent<FallEffect>();
				fall.gravity = 1500.0f;
				
				if (i == 0)
					fall.initialAngle = 15.0f;
				else if (i == bubbles.Count - 1)
					fall.initialAngle = 180.0f - 15.0f;
				else
					fall.initialAngle = Random.Range(15.0f, 175.0f);
				
				fall.initialVelocity = Random.Range(100.0f, 200.0f);
				fall.lowerLimit = _boundRect.bottom;				
			}
			//print(bubbles);//移除球数组中的元素
			_grid.Remove(bubbles[i]);
			//成绩添加
			this.levelscore++;
			this.totalscore++;
				
		}
	}
	
	/*
	 * 计算球链长度
	 */
	private List<Index> GetChain(Index startIndex)
	{
		Bubble shooterBubble = _shooter;
		Bubble.Type shooterType = shooterBubble.type;
		
		List<Index> chainList = new List<Index>();

		ClearVisitedList();
		
		List<Index> dfsList = new List<Index>();
		dfsList.Add(startIndex);
		_visited[startIndex.row, startIndex.col] = true;
	
		while (dfsList.Count != 0) {
			// pop the first entry
			Index current = dfsList[0];
			dfsList.RemoveAt(0);
			
			// add this to the final chain list!
			chainList.Add(current);
			
			Index[] neighbours = Misc.GetNeighbours(current);
			
			foreach (var next in neighbours) {
				if (InNewChain(next, shooterType)) {
					dfsList.Add(next);
					_visited[next.row, next.col] = true;
				}
			}
		}
		
		return chainList;
	}
	
	private void ClearVisitedList()
	{
		for (int i = 0; i < G.rows; i++) {
			for (int j = 0; j < G.cols; j++) {
				_visited[i, j] = false;
			}
		}
	}

	private List<Index> GetUnlinked()
	{
		List<Index> dfsList = new List<Index>();
		
		ClearVisitedList();
		
		for (int i = 0; i < G.cols; i++) {
			if (_grid.Get(0, i) != null) {
				dfsList.Add(new Index(0, i));
				_visited[0, i] = true;
			}
		}
		
		while (dfsList.Count != 0) {
			Index current = dfsList[0];
			dfsList.RemoveAt(0);
			
			Index[] neighbours = Misc.GetNeighbours(current);
			
			foreach (var next in neighbours) {
				if (IsIndexValid(next) &&
					_visited[next.row, next.col] == false &&
					_grid.Get(next) != null) {
					dfsList.Add(next);
					_visited[next.row, next.col] = true;
				}
			}
		}
		
		// final processing! those un-visited bubbles are unlinked ones.
		List<Index> unlinked = new List<Index>();
		for (int i = 0; i < G.rows; i++) {
			for (int j = 0; j < G.cols; j++) {
				if (_grid.Get(i, j) != null && _visited[i, j] == false) {
					unlinked.Add(new Index(i, j));
				}
			}
		}
		
		return unlinked;
	}
	
	private bool IsIndexValid(Index index)
	{
		return index.row >= 0 && index.row < G.rows &&
			index.col >= 0 && index.col < G.cols;
	}
	
	private bool InNewChain(Index next, Bubble.Type type)
	{
		if (IsIndexValid(next) &&
			_visited[next.row, next.col] == false &&
			_grid.Get (next) != null) {
			var bubble = _grid.Get (next);
			
			if (type != Bubble.Type.None && bubble.type == type) {
				return true;
			}
		}
		
		return false;
	}
	/*
	 *获取射击球位置 
	 */
	private Vector3 GetShooterPosition()
	{
		float realHeight = Mathf.Sqrt(3.0f) * (G.rows - 1) * G.radius + 2 * G.radius;
		//Debug.Log(-realHeight / 2.0f - G.radius - 5.0f);
		//return new Vector3(0, 0, -1);
		return new Vector3(0, -realHeight / 2.0f - G.radius - 5.0f /* some delta to make it look nice */, -1);
	}
	/*
	 *获取射击球位置2
	 */
	private Vector3 GetShooterPosition2()
	{
		float realHeight = Mathf.Sqrt(3.0f) * (G.rows - 1) * G.radius + 2 * G.radius;
		//Debug.Log(-realHeight / 2.0f - G.radius - 5.0f);
		//return new Vector3(0, 0, -1);
		return new Vector3(0, -realHeight / 2.0f - G.radius - 15.0f /* some delta to make it look nice */, -1);
	}

	private Vector3 GetNextPosition()
	{
		Vector3 origin = GetShooterPosition();
		origin.x -= G.radius * 2.0f * 2.6f;
		origin.y -= G.radius / 2.0f;
		return origin;
	}
	/*
	 * 加载射击球
	 */
	public void LoadShooterBubble()
	{
		
		if (_grid.Count > 0)
		{
			// with random colors or from a specific sequence!
			if (_next == null)
			{
				_next = GetOneBubbleAtPosition(GetNextPosition());			
				// make it smaller 设定下一个预备球及大小
				_next.transform.localScale = new Vector3(0.8f, 0.8f, 1.0f);
			}
	        //设定射击球及位置
			_shooter = GetOneBubbleAtPosition(GetShooterPosition2(), _next.type);

			Destroy(_next.gameObject);

			_next = GetOneBubbleAtPosition(GetNextPosition());
			// make it smaller 设定下一个预备球及大小
			_next.transform.localScale = new Vector3(0.8f, 0.8f, 1.0f);
		}
		
		_fired = false;
		
	}
	
	private Bubble GetOneBubbleAtPosition(Vector3 position, Bubble.Type type = Bubble.Type.None)
	{
		var go = Instantiate(ball, position, Quaternion.identity) as GameObject;

        if (type == Bubble.Type.None)
        {
        	type = Bubble.GetRandomColorFromList(_grid.GetAllUniqueTypes());
        }

		SpriteRenderer render = go.GetComponent<SpriteRenderer>();
		render.sprite = getBubbleSprite (type);

		Bubble bubble = go.GetComponent<Bubble>();
		bubble.type = type;
		
		return bubble;
	}

    private ParkingStateInfo IsFinalParkingIndex(float speed, float epsilon,
        float x, float y,
        float dx, float dy,
        bool playSound = false)
    {
        bool shouldPark = false;

        float prev_x = x;
        float prev_y = y;

        x += dx * speed;
        y += dy * speed;

        if (x < _boundRect.left + G.radius)
        {
            x = _boundRect.left + G.radius;
            dx *= -1;
            
            if (playSound)
            	AudioManager.Instance.Play(reboundClip);
        }

        if (x > _boundRect.right - G.radius)
        {
            x = _boundRect.right - G.radius;
            dx *= -1;

			if (playSound)
            	AudioManager.Instance.Play(reboundClip);
        }

        if (y > _boundRect.top - G.radius)
        {
            y = _boundRect.top - G.radius;
            shouldPark = true;
        }

        if (!shouldPark && IsCollidingOthers(new Vector3(x, y), epsilon))
            shouldPark = true;

        if (shouldPark)
        {
            Index parkingIndex = Misc.PositionToIndex(_boundRect, new Vector3(x, y));
			
			if (parkingIndex.row + _compressorLevel == G.rows)
			{
				loseCallback();
				return new ParkingStateInfo(shouldPark, x, y, dx, dy);;
			}
			
            if (_grid.Get(parkingIndex) != null)
            {
                // we go backtrack to find the first non-colliding point!
                while (!(Mathf.Approximately(x, prev_x) && Mathf.Approximately(y, prev_y)))
                {
                    // let's try 2 points a step!
                    x -= dx * 2.0f;
                    y -= dy * 2.0f;

                    if (!IsCollidingOthers(new Vector3(x, y), epsilon))
                    {
                    	break;
                    }
                }

                parkingIndex = Misc.PositionToIndex(_boundRect, new Vector3(x, y));
                Vector3 tempPosition = Misc.IndexToPosition(_boundRect, parkingIndex);
                x = tempPosition.x;
                y = tempPosition.y;
            }
        }

        return new ParkingStateInfo(shouldPark, x, y, dx, dy);
    }

	private bool IsCloseEnough(Vector3 pos1, Vector3 pos2, float collisionEpsilon)
	{
		float distX = pos1.x - pos2.x;
		float distY = pos1.y - pos2.y;
		
		return distX * distX + distY * distY <= (2 * G.radius * collisionEpsilon) * (2 * G.radius * collisionEpsilon);
	}

	#region Touch Handlers
	
	public void HandleTouchBegan(Finger f)
	{
		HandleTouchMoved(f);
	}
	
	public void HandleTouchMoved(Finger f)
	{
		Vector3 touchPosition = Camera.main.ScreenToWorldPoint(new Vector3(f.x, f.y));
		Vector3 midPosition = GetShooterPosition();

		if (touchPosition.y >= midPosition.y)
		{
			_shootingAngle = Mathf.Rad2Deg * Mathf.Atan2(touchPosition.y - midPosition.y, touchPosition.x - midPosition.x);
			_shootingAngle = Mathf.Clamp(_shootingAngle, 0.0f + G.shootingMinAngle, 180.0f - G.shootingMinAngle);
			
			cannon.transform.rotation = Quaternion.Euler(0, 0, _shootingAngle - 90.0f);
		}
	}
	
	public void HandleTouchCanceled(Finger f)
	{
		// do nothing, we don't fire the ball.
	}
	
	public void HandleTouchEnded(Finger f)
	{
		StartFire();
	}

	#endregion

	private void OnChain(Index index)
	{
		List<Index> chains = GetChain(index);
		if (chains.Count >= 3)
		{
			RemoveBubbles(chains, RemoveType.ChainRemoval);
		
			AudioManager.Instance.Play(destroyGroupClip);
		}
		else
		{
			AudioManager.Instance.Play(stickClip);
		}
	}

    private void OnUnlink(Index index)
    {
		List<Index> unlinked = GetUnlinked();
		RemoveBubbles(unlinked, RemoveType.UnlinkRemoval);
    }
		
	/*
	 * 胜利或者失败
	 */
	private void WinOrLose()
	{		
		if (_grid.Count == 0)
		{
			// win
			winCallback();
			return;
		}
		
		if (_grid.MaxRow + _compressorLevel >= G.rows)
		{
			
			loseCallback();
			return;
		}
	}
	
	private void winCallback()
	{
		// we just reload again
		this.winPanel.SetActive(true);
		GameObject.Find("levelScorewin").GetComponent<Text>().text = this.levelscore.ToString();
		this.startgameflag = 0;
		//LoadNextLevel ();
	}
	
	private void loseCallback()
	{
		this.failPanel.SetActive(true);
		//GetComponent
		GameObject.Find("levelScorelose").GetComponent<Text>().text= this.levelscore.ToString();
		this.startgameflag = 0;
		//LoadNextLevel (this.GlobalLevel);
	}
	
	/// <summary>
	/// get the sprite according to its bubble type
	/// </summary>
	/// <returns>The bubble sprite.</returns>
	/// <param name="type">Type.</param>
	private Sprite getBubbleSprite(Bubble.Type type)
	{
		switch (type) {
		case Bubble.Type.Color1:
				return _bubble_1;

		case Bubble.Type.Color2:
				return _bubble_2;

		case Bubble.Type.Color3:
				return _bubble_3;

		case Bubble.Type.Color4:
				return _bubble_4;

		case Bubble.Type.Color5:
				return _bubble_5;

		case Bubble.Type.Color6:
				return _bubble_6;

		case Bubble.Type.Color7:
				return _bubble_7;

		case Bubble.Type.Color8:
				return _bubble_8;
		}

		return null;
	}


	public void nextlevel(int intype)
    {
		if (intype==0) this.winPanel.SetActive(false);
		else this.failPanel.SetActive(false);
		LoadNextLevel();
	}
	public void playAgain(int intype)
    {
		if (intype == 0) this.winPanel.SetActive(false);
		else this.failPanel.SetActive(false);
		LoadNextLevel(this.GlobalLevel);
	}
	public void returnhome()
    {
		SceneManager.LoadScene("MainMenuScene");
	}
}
