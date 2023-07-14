array(
    0: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_Variable(
                name: array
            )
            expr: Expr_Array(
                items: array(
                )
            )
        )
    )
    1: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_ArrayDimFetch(
                var: Expr_Variable(
                    name: array
                )
                dim: null
            )
            expr: Scalar_String(
                value: safe
            )
        )
    )
    2: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_ArrayDimFetch(
                var: Expr_Variable(
                    name: array
                )
                dim: null
            )
            expr: Expr_ArrayDimFetch(
                var: Expr_Variable(
                    name: _GET
                )
                dim: Scalar_String(
                    value: userData
                )
            )
        )
    )
    3: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_ArrayDimFetch(
                var: Expr_Variable(
                    name: array
                )
                dim: null
            )
            expr: Scalar_String(
                value: safe
            )
        )
    )
    4: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_Variable(
                name: tainted
            )
            expr: Expr_ArrayDimFetch(
                var: Expr_Variable(
                    name: array
                )
                dim: Scalar_LNumber(
                    value: 1
                )
            )
        )
    )
    5: Stmt_Expression(
        expr: Expr_Assign(
            var: Expr_Variable(
                name: tainted
            )
            expr: Expr_Cast_Double(
                expr: Expr_Variable(
                    name: tainted
                )
            )
        )
    )
    6: Stmt_Echo(
        exprs: array(
            0: Expr_Variable(
                name: tainted
            )
        )
    )
)
