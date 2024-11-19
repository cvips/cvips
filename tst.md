
# SVD via Eigenvectors
<!-- 
#Why SVD may give invalid decompositions:

Eigendecomposition:

Consider eigendecomposition of $A$. $A = V \Lambda U$. We first find the eigenvectors of $A$ to form $V$. Then, we invert it to find $U = V^{-1}$.

However, we CANNOT treat the eigendecomposition as two separate steps.
Suppose we compute the eigenvectors of $A$ to form $V$. And then as a second, INDEPENDENT step, find the RIGHT eigenvectors of $A$ to find $U$. There is no guarantee that $U$ and $V$ are inverses. So, $A$ may or may not be $V\Lambda U$.

So, the correct approach is to find the eigenvectors of $A$ to form $V$, then invert it to get $U$. This allows U and V to be inverses.

In other words, not every $U$ and $V$ work, $U$ and $V$ must be inverses.

This idea is also why SVD sometimes doesn't work properly... -->

<!-- SVD: -->

In SVD, $A = UΣV^T$.

We saw that to find the eigendecomposition of $AA^T$ to get $U$. As a SEPARATE, INDEPENDENT step, we find $V$ through the eigendecomposition of $A^TA$. However, we cannot guarantee any relationship between $U$ and $V$ (since the two steps are independent). So, this may lead to incorrect SVDs.

In other words, $U$ and $V$ must have a relationship and not EVERY possible $U$ and $V$ combination will work.

# How to fix SVD

Instead of treating the problem as two separate eigendecompositions, we find $V$ OR $U$ (depending on the matrix $A$) using eigendecomposition, then solve for the other one.

# Tall Matrices

If $A$ is a "tall" matrix (more rows than columns), then we find $U$ first using eigendecomposition of $AA^T$. Then, plug in $U$, $A$, $\Sigma$ to find $V$:

$A = UΣV^T \rightarrow  U^T A = \Sigma V^T$

If $A$ is a $M \times N$ matrix, $M > N$ since it is tall. So, $U$ is $M \times M$, $\Sigma$ is $M \times N$ and $V^T$ is $N \times N$.

Thus, $U^T A$ and $\Sigma V^T$ are both $M \times N$ matrices with more rows than columns.
It may be difficult to work with matrices that are not square, but $U^T A$ and $\Sigma V^T$ contain $N-M$ rows of zeros. By removing these corresponding rows, we obtain $M \times M$ size matrices and can solve for $V^T$.

# Example of Tall Matrix SVD

Let $A = \begin{bmatrix}1 &-1 \\ 0& 1 \\ 1& 0 \end{bmatrix}$

We find the eigendecomposition of $AA^T$ to find $U$.

$AA^T = \begin{bmatrix}\frac{2}{\sqrt{6}} &0 & \frac{1}{\sqrt{3}} \\ -\frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}}  \\ \frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}}  \end{bmatrix} \begin{bmatrix}3 & 0 & 0 \\ 0& 1&0 \\ 0& 0 & 0 \end{bmatrix} \begin{bmatrix}\frac{2}{\sqrt{6}} &0 & \frac{1}{\sqrt{3}} \\ -\frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}}  \\ \frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}}  \end{bmatrix}^T$

The singular values are $\sqrt{3}$ and $1$.

$U = \begin{bmatrix}\frac{2}{\sqrt{6}} &0 & \frac{1}{\sqrt{3}} \\ -\frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}}  \\ \frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}}  \end{bmatrix}$

and $\Sigma = \begin{bmatrix}\sqrt{3} & 0 \\ 0 & 1 \\ 0 & 0 \end{bmatrix}$

Using this, we find $U^TA = \Sigma V^T$.

$U^TA =  \begin{bmatrix}\frac{3}{\sqrt{6}} & -\frac{3}{\sqrt{6}} \\ \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \\ 0 & 0 \end{bmatrix}$

$\Sigma V^T= \begin{bmatrix}\begin{bmatrix}\sqrt{3} & 0 \\ 0 & 1\end{bmatrix}V^T\\ 0 \:\:\:\: \:\:0 \end{bmatrix}$

Removing the last row of zeros yields
$\begin{bmatrix}\frac{3}{\sqrt{6}} & -\frac{3}{\sqrt{6}} \\ \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \end{bmatrix} = \begin{bmatrix}\sqrt{3} & 0 \\ 0 & 1\end{bmatrix}V^T $

Solving yields $V^T = \begin{bmatrix}\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \end{bmatrix}$.

So, $A =  \begin{bmatrix}\frac{2}{\sqrt{6}} &0 & \frac{1}{\sqrt{3}} \\ -\frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}}  \\ \frac{1}{\sqrt{6}} &\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}}  \end{bmatrix}\begin{bmatrix}\sqrt{3} & 0 \\ 0 & 1 \\ 0 & 0 \end{bmatrix}\begin{bmatrix}\frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \end{bmatrix}$


# Wide matrices
If $A$ is a "wide" matrix (more columns than rows), then we find $V$ first using eigendecomposition of $A^TA$. Then plug in $V$, $A$, $\Sigma$ to find $U$.

$A = UΣV^T \rightarrow  AV = U\Sigma$

If $A$ is a $M \times N$ matrix, $M < N$ since it is wide. So, $U$ is $M \times M$, $\Sigma$ is $M \times N$ and $V^T$ is $N \times N$.

Thus, $AV$ and $U \Sigma$ are both $M \times N$ matrices with more columns than rows.

It may be difficult to work with matrices that are not square, but $AV$ and $U\Sigma$ contain $M-N$ columns of zeros. By removing these corresponding columns, we obtain $N \times N$ size matrices and can solve for $U$. (An alternative approach is just to take the pseudoinverse).

# Example of Wide Matrix SVD


Exercise.  $A = \begin{bmatrix}1 & 0 & 1\\ -1 & 1 & 0\end{bmatrix}$

(Here, we find the eigendecomposition of $AA^T$ to find $V$ first and solve for $U$ from $U\Sigma = AV$) 
