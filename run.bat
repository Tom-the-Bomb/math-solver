@ECHO off

IF "%1"=="--release" (
    py -m hypercorn backend.app:app
) else (
    py -m backend
)