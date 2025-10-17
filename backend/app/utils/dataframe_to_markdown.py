from tabulate import tabulate
import pandas as pd


def beautify_table(df: pd.DataFrame) -> pd.DataFrame:
    """Converts all datetime columns to string.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert.

    Returns
    -------
    pd.DataFrame
        The converted DataFrame.
    """
    # TODO. refactor. Double loop...
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # TODO. bad solution.
            df[column] = (
                df[column].astype(str).apply(lambda x: x.replace(" 00:00:00+00:00", ""))
            )
    columns_rename_dict = {col: col.replace("_", " ").title() for col in df.columns}
    df.rename(columns=columns_rename_dict, inplace=True)
    return df


def dataframe_to_markdown(data: pd.DataFrame):
    """
    Process a pandas dataframe into markdown.

    Parameters
    ----------
    data :  pandas.DataFrame
        Dataframe to be formatted.

    Returns
    -------
    str
        Markdown string format of dataframe.
    """
    beautify_table(data)
    try:
        markdown_table = tabulate(
            data, headers="keys", tablefmt="grid", showindex=False, maxcolwidths=60
        )
    except Exception as error:
        markdown_table = tabulate(
            data,
            headers="keys",
            tablefmt="grid",
            showindex=False,
        )
    markdown_table = f"\n{markdown_table}\n"
    return markdown_table
