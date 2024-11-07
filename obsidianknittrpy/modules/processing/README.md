# This directory contains all modular processing which can be run during an execution

Currently, the module-system is in early development. Multiple things can and will change; and it is only applied to the processing-pipeline itself so far.

The intention is to make expansion of the processing-pipeline significantly simpler and easier to maintain.

## required conversion-steps

```
ConvertSRC_SYNTAX_V4 DONE
>
processTags DONE
>
processAbstract DONE, and disabled. 
```

## format-specific conversion-steps

QMD:
    convertBookdownToQuartoReferencing
    ProcessDiagramCodeblocks                                  DONE
    moveEquationreferencesToEndofBlock
    moveEquationLabelsUpIntoLatexEquation
    fixCitationpathing
    fixNullFields (in frontmatter)                   DONE
    ProcessInvalidQuartoFrontmatterFields            DONE

RMD:
    cleanLatexEnvironmentsforRMarkdown
    (fixNullFields) - should always be run          DONE

QMD:
    quartopurgeTags - does nothing, can be ignored.

QMD (args.noContent)
    quartopurgeContents